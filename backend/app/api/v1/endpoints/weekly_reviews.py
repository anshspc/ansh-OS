from typing import Any, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.weekly_review import GenerateWeeklyReviewRequest, WeeklyReviewResponse
from app.services.weekly_review_service import WeeklyReviewService

router = APIRouter()


@router.get("", response_model=List[WeeklyReviewResponse])
async def get_weekly_reviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await WeeklyReviewService.get_reviews(db=db, user_id=current_user.id)


@router.post("/generate", response_model=WeeklyReviewResponse, status_code=status.HTTP_201_CREATED)
async def generate_weekly_review(
    payload: GenerateWeeklyReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await WeeklyReviewService.generate_weekly_review(db=db, user_id=current_user.id, request=payload)


@router.get("/{review_id}", response_model=WeeklyReviewResponse)
async def get_review_by_id(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await WeeklyReviewService.get_review_by_id(db=db, user_id=current_user.id, review_id=review_id)
