"""
Authentication routes: register, login, and user info
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from handlers.auth import get_password_hash, verify_password, create_access_token, get_current_active_user
from schemas.schemas import UserCreate, UserResponse, Token, LogMessage
from handlers.logger import log_message
from handlers.database import get_db
from schemas.models import User

from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/api/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user"""
    db = get_db()
    
    existing_user = await db.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = await db.get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    await db.create_user(new_user)
    
    return UserResponse(
        username=new_user.username,
        email=new_user.email,
        created_at=new_user.created_at,
        is_active=new_user.is_active
    )

@router.post("/api/token", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get JWT access token"""
    db = get_db()
    user = await db.get_user_by_username(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        msg = LogMessage.from_request(request, user.username, 401)
        await log_message(msg.to_message)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    msg = LogMessage.from_request(request, user.username, 200)
    await log_message(msg.to_message)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/api/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        is_active=current_user.is_active
    )