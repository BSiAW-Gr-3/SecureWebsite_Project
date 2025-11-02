"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
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
    chat_name: str
    message: str


class ChatMessageResponse(BaseModel):
    username: str
    message: str
    timestamp: datetime


class LogMessage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    method: str
    path: str
    status_code: int
    direct_ip: str  
    origin_ip: Optional[str] = None  
    user_agent: Optional[str] = None
    username: Optional[str] = None

    @classmethod
    def from_middleware(cls, request: Request, response: Response) -> classmethod:
        direct_ip = request.client.host if request.client else "unknown"
        origin_ip = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for")
        
        if origin_ip and "," in origin_ip:
            origin_ip = origin_ip.split(",")[0].strip()

        return cls(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            direct_ip=direct_ip,
            origin_ip=origin_ip,
            user_agent=request.headers.get("user-agent"),
        )

    @classmethod
    def from_request(cls, request: Request, username: str, code: int = 0) -> classmethod:
        direct_ip = request.client.host if request.client else "unknown"
        origin_ip = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for")
        
        if origin_ip and "," in origin_ip:
            origin_ip = origin_ip.split(",")[0].strip()

        return cls(
            method=request.method,
            path=request.url.path,
            status_code=code,  
            direct_ip=direct_ip,
            origin_ip=origin_ip,
            user_agent=request.headers.get("user-agent"),
            username=username
        )

    @property
    def to_message(self) -> str:
        display_ip = self.origin_ip if self.origin_ip else self.direct_ip
        
        msg = f"IP: {display_ip}"
        if self.origin_ip and self.origin_ip != self.direct_ip:
            msg += f" (via LB: {self.direct_ip})"

        if self.username:
            msg += f" | User: {self.username}"
            
        return (f"{msg} | Method: {self.method} | Path: {self.path} | "
                f"Status: {self.status_code} | UA: {self.user_agent or 'unknown'}")
