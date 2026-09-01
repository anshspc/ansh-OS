from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class HabitLogCreate(BaseModel):
    logged_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    completed: bool = True
    value: float = 1.0
    notes: Optional[str] = None


class HabitLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    habit_id: str
    user_id: str
    logged_date: str
    completed: bool
    value: float
    notes: Optional[str] = None
    created_at: datetime


class HabitCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    goal_id: Optional[str] = None
    frequency: str = Field(default="daily")
    target_days: List[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6])
    reminder_time: Optional[str] = None
    color: str = Field(default="#8b5cf6")
    icon: str = Field(default="activity")


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    goal_id: Optional[str] = None
    frequency: Optional[str] = None
    target_days: Optional[List[int]] = None
    reminder_time: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class HabitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    goal_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    frequency: str
    target_days: List[int]
    reminder_time: Optional[str] = None
    streak_count: int
    best_streak: int
    color: str
    icon: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    today_completed: Optional[bool] = False
    completion_rate_30d: Optional[float] = 0.0
    recent_logs: List[HabitLogResponse] = Field(default_factory=list)
