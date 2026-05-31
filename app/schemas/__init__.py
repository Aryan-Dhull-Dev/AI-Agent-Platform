# app/schemas/__init__.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ============ Chat Session Schemas ============
class ChatSessionBase(BaseModel):
    title: Optional[str] = "New Chat"

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None

# ============ Message Schemas ============
class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    session_id: int

class MessageResponse(MessageBase):
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ Chat Request Schemas ============
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    session_id: int
    session_title: str
    tokens_used: int

# ============ Agent Execution Schemas ============
class AgentExecutionResponse(BaseModel):
    id: int
    prompt: str
    response: str
    tokens_total: int
    cost_usd: float
    created_at: datetime
    
    class Config:
        from_attributes = True