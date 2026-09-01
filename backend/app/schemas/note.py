from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(default="")
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_pinned: bool = False


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    title: str
    content: str
    tags: List[str]
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
