from typing import Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import ActivityLogResponse, DashboardSummaryResponse, ProductivityScoreResponse
from app.services.activity_service import ActivityService
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/dashboard-summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await AnalyticsService.get_dashboard_summary(
        db=db,
        user_id=current_user.id,
        user_name=current_user.full_name,
    )


@router.get("/productivity-score", response_model=ProductivityScoreResponse)
async def get_productivity_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await AnalyticsService.compute_productivity_score(
        db=db,
        user_id=current_user.id,
    )


@router.get("/activities", response_model=List[ActivityLogResponse])
async def get_activities(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ActivityService.get_recent_activities(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )
