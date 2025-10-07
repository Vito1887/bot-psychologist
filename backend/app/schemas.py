from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserRegisterTelegramRequest(BaseModel):
    telegram_id: str
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TaskResponse(BaseModel):
    id: int
    text: str
    sent_at: datetime
    status: str

    class Config:
        from_attributes = True


class ProgressResponse(BaseModel):
    total: int
    completed: int
    today_completed: int
    week_completed: int
    month_completed: int


class CompleteTaskResponse(BaseModel):
    success: bool
    task: TaskResponse
