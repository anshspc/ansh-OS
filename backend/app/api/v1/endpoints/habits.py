from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.habit import HabitCreate, HabitLogCreate, HabitResponse, HabitUpdate
from app.services.habit_service import HabitService

router = APIRouter()


@router.get("", response_model=List[HabitResponse])
async def get_habits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await HabitService.get_habits(db=db, user_id=current_user.id)


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    payload: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await HabitService.create_habit(db=db, user_id=current_user.id, payload=payload)


@router.get("/heatmap", response_model=Dict[str, int])
async def get_habit_heatmap(
    days: int = Query(default=365, ge=30, le=730),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await HabitService.get_heatmap_data(db=db, user_id=current_user.id, days=days)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit_by_id(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await HabitService.get_habit_by_id(db=db, user_id=current_user.id, habit_id=habit_id)


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: str,
    payload: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await HabitService.update_habit(db=db, user_id=current_user.id, habit_id=habit_id, payload=payload)


@router.post("/{habit_id}/log", response_model=HabitResponse)
async def log_habit(
    habit_id: str,
    payload: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await HabitService.log_habit(db=db, user_id=current_user.id, habit_id=habit_id, payload=payload)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await HabitService.delete_habit(db=db, user_id=current_user.id, habit_id=habit_id)
