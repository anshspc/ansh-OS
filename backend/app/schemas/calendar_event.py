from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class CalendarEventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_all_day: bool = False
    event_type: str = Field(default="focus")
    color: str = Field(default="#6366f1")
    location: Optional[str] = None
    recurrence: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_all_day: Optional[bool] = None
    event_type: Optional[str] = None
    color: Optional[str] = None
    location: Optional[str] = None
    recurrence: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class CalendarEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_all_day: bool
    event_type: str
    color: str
    location: Optional[str] = None
    recurrence: Optional[str] = None
    metadata_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
