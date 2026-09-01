from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class WeeklyReviewCreate(BaseModel):
    start_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    summary: str
    wins: List[str] = Field(default_factory=list)
    bottlenecks: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    productivity_score: float = Field(default=0.0, ge=0.0, le=100.0)
    stats: Dict[str, Any] = Field(default_factory=dict)


class WeeklyReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    start_date: str
    end_date: str
    summary: str
    wins_json: List[str]
    bottlenecks_json: List[str]
    recommendations_json: List[str]
    productivity_score: float
    stats_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class GenerateWeeklyReviewRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
