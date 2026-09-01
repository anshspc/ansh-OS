from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductivityBreakdown(BaseModel):
    task_completion: float = Field(description="Score component for task completion rate (0-25)")
    goal_progress: float = Field(description="Score component for goal milestones (0-20)")
    focus_consistency: float = Field(description="Score component for scheduled focus time (0-20)")
    habit_consistency: float = Field(description="Score component for daily habit streaks (0-20)")
    deadline_management: float = Field(description="Score component for timely deliveries (0-15)")


class ProductivityScoreResponse(BaseModel):
    total_score: float = Field(description="Overall productivity score from 0 to 100")
    grade: str = Field(description="Productivity tier: S, A, B, C, D")
    breakdown: ProductivityBreakdown
    explanation: str
    insights: List[str]
    trend_compared_to_last_week: float


class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Dict[str, Any]
    created_at: datetime


class DashboardSummaryResponse(BaseModel):
    greeting: str
    today_date: str
    productivity_score: float
    productivity_grade: str
    tasks_summary: Dict[str, int]
    habits_summary: Dict[str, int]
    active_projects_count: int
    active_goals_count: int
    today_focus_tasks: List[Dict[str, Any]]
    today_events: List[Dict[str, Any]]
    ai_daily_insight: str
    recent_activities: List[ActivityLogResponse]
