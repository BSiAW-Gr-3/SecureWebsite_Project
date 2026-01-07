"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, IPvAnyAddress, field_validator
from fastapi import Request, Response
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters long')
        return v

class UserResponse(BaseModel):
    username: str
    email: EmailStr
    created_at: datetime
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ChatMessageCreate(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    username: str
    message: str
    timestamp: datetime

class LogMessage(BaseModel):
    method: str
    path: str
    status_code: int
    ip_address: IPvAnyAddress
    user_agent: Optional[str] = None

    @classmethod
    def from_request(cls, request: Request, response: Response):
        """Helper to create the log model from FastAPI objects"""
        return cls(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    @property
    def to_message(self) -> str:
        return (f"IP: {self.ip_address} | Method: {self.method} | "
                f"Path: {self.path} | User-Agent: {self.user_agent or 'unknown'} | "
                f"Status: {self.status_code}")
