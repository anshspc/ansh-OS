from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserPreferences(BaseModel):
    theme: str = Field(default="system")
    working_hours_start: str = Field(default="09:00")
    working_hours_end: str = Field(default="18:00")
    productivity_style: str = Field(default="deep_work")
    ai_creativity: str = Field(default="balanced")
    daily_reminder: bool = Field(default=True)


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="Password must be at least 6 characters")
    full_name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    has_onboarded: Optional[bool] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    has_onboarded: bool
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
