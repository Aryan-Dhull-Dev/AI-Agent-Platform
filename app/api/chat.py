# app/api/chat.py

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import os

from app.db.session import get_db
from app.db.models import User, ChatSession, Message, AgentExecution
from app.schemas import ChatRequest, ChatResponse
from app.core.auth import get_current_user 
from app.services.ai_service import AIService
from app.services.prompt_manager import PromptManager
from fastapi import StreamingResponse

router = APIRouter(prefix="/api", tags=["chat"])

# Initialize AI service
ai_service = AIService()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: Optional[str] = None  # "code", "architecture", "debugging", or None

class ChatResponse(BaseModel):
    response: str
    session_id: int
    session_title: str
    tokens_used: int
    model: str

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # Add auth dependency
    db: AsyncSession = Depends(get_db)
):
    """
    Send message to AI agent (Groq + Llama 3.1 70B)
    
    - Auth required
    - Supports conversation history
    - Tracks token usage
    """
    
    # Get or create chat session
    if request.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        # Create new session
        session = ChatSession(user_id=current_user.id, title="New Chat")
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
    # Get conversation history
    result = await db.execute(
        select(Message).where(Message.session_id == session.id).order_by(Message.created_at.desc()).limit(10)
    )
    history = [{"role": m.role, "content": m.content} for m in result.scalars().all()]
    
    # Create messages for AI
    messages = PromptManager.create_conversation_messages(
        user_message=request.message,
        history=history,
        mode=request.mode
    )
    
    # Call AI service
    try:
        ai_response = await ai_service.chat(messages=messages)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )
        
    # Save user message
    user_message = Message(
        session_id=session.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    
    # Save assistant message
    assistant_message = Message(
        session_id=session.id,
        role="assistant",
        content=ai_response["response"]
    )
    db.add(assistant_message)
    
    # Save agent execution record
    agent_execution = AgentExecution(
        user_id=current_user.id,
        session_id=session.id,
        prompt=request.message,
        response=ai_response["response"],
        tokens_input=ai_response["token_usage"]["tokens_input"],
        tokens_output=ai_response["token_usage"]["tokens_output"],
        tokens_total=ai_response["token_usage"]["tokens_total"],
        cost_usd=ai_response["token_usage"]["cost_usd"],
        model_used=ai_response["model"]
    )
    db.add(agent_execution)
    
    await db.commit()
    
    return ChatResponse(
        response=ai_response["response"],
        session_id=session.id,
        session_title=session.title,
        tokens_used=ai_response["token_usage"]["tokens_total"],
        model=ai_response["model"]
    )


@router.post("/stream-chat")
async def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send message to AI with streaming (token-by-token)
    
    - Auth required
    - SSE streaming for real-time UI updates
    """
    
    # Get or create session (same as sync chat)
    if request.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        session = ChatSession(user_id=current_user.id, title="New Chat")
        db.add(session)
        await db.commit()
        await db.refresh(session)
    
    # Get history
    result = await db.execute(
        select(Message).where(Message.session_id == session.id).order_by(Message.created_at.desc()).limit(10)
    )
    history = [{"role": m.role, "content": m.content} for m in result.scalars().all()]
    
    # Create messages
    messages = PromptManager.create_conversation_messages(
        user_message=request.message,
        history=history,
        mode=request.mode
    )
    
    # Stream tokens
    async def generate_stream():
        full_response = ""
        
        try:
            stream = await ai_service.stream_chat(messages=messages)
            
            async for chunk in stream:
                if chunk.get("done"):
                    # Save full response to DB
                    user_msg = Message(session_id=session.id, role="user", content=request.message)
                    assistant_msg = Message(session_id=session.id, role="assistant", content=full_response)
                    db.add(user_msg)
                    db.add(assistant_msg)
                    
                    usage = chunk["token_usage"]
                    agent_exec = AgentExecution(
                        user_id=current_user.id,
                        session_id=session.id,
                        prompt=request.message,
                        response=full_response,
                        tokens_input=usage["tokens_input"],
                        tokens_output=usage["tokens_output"],
                        tokens_total=usage["tokens_total"],
                        cost_usd=usage["cost_usd"],
                        model_used=ai_service.model
                    )
                    db.add(agent_exec)
                    await db.commit()
                    
                    yield f'data: {"done": true, "tokens": {usage["tokens_total"]}}\n\n'
                else:
                    token = chunk["token"]
                    full_response += token
                    yield f'data: {token}'
        except Exception as e:
            yield f'data: {"error": "{str(e)}"}\n\n'
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
    
@router.get("/model-info")
async def get_model_info():
    """Get information about current AI model"""
    return await ai_service.get_model_info()

@router.get("/agents")
async def list_agents():
    """List agents endpoint (placeholder for Day 5)"""
    return {
        "agents": [
            {"name": "planner", "status": "pending"},
            {"name": "tool_executor", "status": "pending"},
            {"name": "responder", "status": "pending"}
        ],
        "message": "Agents will be implemented on Day 5"
    }
    
@router.get("/history")
async def get_chat_history(
    session_id: int,
    current_user: User = Depends(get_current_user),  # Add auth
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a session"""
    # Verify session belongs to user
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get messages
    result = await db.execute(
        select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    
    return {
        "session_id": session.id,
        "title": session.title,
        "messages": [{"role": m.role, "content": m.content} for m in messages]
    }