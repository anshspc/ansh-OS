from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SubtaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    is_completed: bool = False
    position: int = 0


class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    position: Optional[int] = None


class SubtaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    title: str
    is_completed: bool
    position: int
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    status: str = Field(default="todo")
    priority: str = Field(default="medium")
    due_date: Optional[datetime] = None
    estimated_duration: int = Field(default=30, ge=1)
    tags: List[str] = Field(default_factory=list)
    recurring: bool = False
    recurrence_rule: Optional[str] = None
    subtasks: Optional[List[SubtaskCreate]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    tags: Optional[List[str]] = None
    recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    position: Optional[int] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[datetime] = None
    estimated_duration: int
    actual_duration: int
    tags: List[str]
    recurring: bool
    recurrence_rule: Optional[str] = None
    position: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    subtasks: List[SubtaskResponse] = Field(default_factory=list)


class TaskBatchUpdate(BaseModel):
    task_ids: List[str]
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    project_id: Optional[str] = None
