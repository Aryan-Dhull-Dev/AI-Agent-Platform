# app/api/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.db.session import get_db
from app.db.models import User, ChatSession
from app.schemas import UserCreate, UserLogin, UserResponse, Token, ChatSessionResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and get access token"""
    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    # Create default chat session for new user
    result = await db.execute(select(ChatSession).where(ChatSession.user_id == user.id))
    sessions = result.scalars().all()
    if not sessions:
        default_session = ChatSession(user_id=user.id, title="First Chat")
        db.add(default_session)
        await db.commit()
        await db.refresh(default_session)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/sessions", response_model=list[ChatSessionResponse])
async def get_user_sessions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get all chat sessions for current user"""
    result = await db.execute(select(ChatSession).where(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()))
    sessions = result.scalars().all()
    return sessions