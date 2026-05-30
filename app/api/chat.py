# app/api/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint (placeholder for Day 3)"""
    # TODO: Implement AI chat on Day 3
    return ChatResponse(
        response=f"Echo: {request.message} (AI not integrated yet)",
        session_id=request.session_id or "default"
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