from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TimeBlockSchema(BaseModel):
    id: str
    start_time: str
    end_time: str
    title: str
    type: str
    task_id: Optional[str] = None
    completed: bool = False


class DailyPlanCreate(BaseModel):
    plan_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    summary: Optional[str] = None
    time_blocks: List[TimeBlockSchema] = Field(default_factory=list)
    focus_areas: List[str] = Field(default_factory=list)
    status: str = Field(default="generated")


class DailyPlanUpdate(BaseModel):
    summary: Optional[str] = None
    time_blocks: Optional[List[TimeBlockSchema]] = None
    focus_areas: Optional[List[str]] = None
    status: Optional[str] = None


class DailyPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    plan_date: str
    summary: Optional[str] = None
    time_blocks_json: List[Dict[str, Any]]
    focus_areas_json: List[str]
    status: str
    created_at: datetime
    updated_at: datetime


class GenerateDailyPlanRequest(BaseModel):
    date: Optional[str] = None
    preferred_start_time: Optional[str] = "09:00"
    preferred_end_time: Optional[str] = "18:00"
    focus_goal_id: Optional[str] = None
