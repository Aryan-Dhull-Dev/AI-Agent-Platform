# app/api/chat.py

from fastapi import APIRouter, HTTPException, Depends
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

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # Add auth dependency
    db: AsyncSession = Depends(get_db)
):
    """Chat endpoint (AI integration on Day 3)"""
    
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
    
    # Save user message
    user_message = Message(
        session_id=session.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    
    # TODO: Add AI response on Day 3
    assistant_message_content = f"Echo: {request.message} (AI not integrated yet)"
    
    # Save assistant message
    assistant_message = Message(
        session_id=session.id,
        role="assistant",
        content=assistant_message_content
    )
    db.add(assistant_message)
    
    # Save agent execution record
    agent_execution = AgentExecution(
        user_id=current_user.id,
        session_id=session.id,
        prompt=request.message,
        response=assistant_message_content,
        tokens_input=10,
        tokens_output=20,
        tokens_total=30,
        cost_usd=0.0,
        model_used=os.getenv("AI_MODEL", "placeholder")
    )
    db.add(agent_execution)
    
    await db.commit()
    
    return ChatResponse(
        response=assistant_message_content,
        session_id=session.id,
        session_title=session.title,
        tokens_used=30
    )

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