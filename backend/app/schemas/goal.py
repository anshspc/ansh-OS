from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class GoalMilestoneCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    due_date: Optional[datetime] = None
    position: int = 0


class GoalMilestoneUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    position: Optional[int] = None


class GoalMilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    goal_id: str
    title: str
    is_completed: bool
    due_date: Optional[datetime] = None
    position: int
    created_at: datetime
    updated_at: datetime


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(default="career")
    target_date: Optional[datetime] = None
    status: str = Field(default="in_progress")
    color: str = Field(default="#10b981")
    icon: str = Field(default="target")
    metrics: Dict[str, Any] = Field(default_factory=dict)
    milestones: Optional[List[GoalMilestoneCreate]] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    target_date: Optional[datetime] = None
    progress: Optional[float] = None
    status: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    category: str
    target_date: Optional[datetime] = None
    progress: float
    status: str
    color: str
    icon: str
    metrics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    milestones: List[GoalMilestoneResponse] = Field(default_factory=list)
    linked_projects_count: Optional[int] = 0
    linked_tasks_count: Optional[int] = 0
