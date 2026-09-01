from datetime import date
from typing import Any, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.models.user import User
from app.schemas.daily_plan import DailyPlanResponse, DailyPlanUpdate, GenerateDailyPlanRequest
from app.services.daily_plan_service import DailyPlanService

router = APIRouter()


@router.get("/{plan_date}", response_model=DailyPlanResponse)
async def get_daily_plan(
    plan_date: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    plan = await DailyPlanService.get_daily_plan_by_date(db=db, user_id=current_user.id, plan_date=plan_date)
    if not plan:
        # Auto generate on the fly if not exists
        plan = await DailyPlanService.generate_daily_plan(
            db=db, user_id=current_user.id, request=GenerateDailyPlanRequest(date=plan_date)
        )
    return plan


@router.post("/generate", response_model=DailyPlanResponse, status_code=status.HTTP_201_CREATED)
async def generate_daily_plan(
    payload: GenerateDailyPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await DailyPlanService.generate_daily_plan(db=db, user_id=current_user.id, request=payload)


@router.put("/{plan_id}", response_model=DailyPlanResponse)
async def update_daily_plan(
    plan_id: str,
    payload: DailyPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await DailyPlanService.update_daily_plan(
        db=db, user_id=current_user.id, plan_id=plan_id, payload=payload
    )
