from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MilestoneCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    position: int = 0


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    position: Optional[int] = None


class MilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: bool
    position: int
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    goal_id: Optional[str] = None
    status: str = Field(default="active")
    color: str = Field(default="#3b82f6")
    icon: str = Field(default="folder")
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    milestones: Optional[List[MilestoneCreate]] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    goal_id: Optional[str] = None
    status: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    progress: Optional[float] = None
    tags: Optional[List[str]] = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    goal_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    color: str
    icon: str
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    progress: float
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    milestones: List[MilestoneResponse] = Field(default_factory=list)
    tasks_count: Optional[int] = 0
    completed_tasks_count: Optional[int] = 0
