from typing import Any, List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.goal import (
    GoalCreate, GoalMilestoneCreate, GoalMilestoneResponse, GoalMilestoneUpdate, GoalResponse, GoalUpdate
)
from app.services.goal_service import GoalService

router = APIRouter()


@router.get("", response_model=List[GoalResponse])
async def get_goals(
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await GoalService.get_goals(db=db, user_id=current_user.id, category=category, status=status)


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await GoalService.create_goal(db=db, user_id=current_user.id, payload=payload)


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal_by_id(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await GoalService.get_goal_by_id(db=db, user_id=current_user.id, goal_id=goal_id)


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    payload: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await GoalService.update_goal(db=db, user_id=current_user.id, goal_id=goal_id, payload=payload)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await GoalService.delete_goal(db=db, user_id=current_user.id, goal_id=goal_id)


@router.post("/{goal_id}/milestones", response_model=GoalMilestoneResponse, status_code=status.HTTP_201_CREATED)
async def add_milestone(
    goal_id: str,
    payload: GoalMilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await GoalService.add_milestone(db=db, user_id=current_user.id, goal_id=goal_id, payload=payload)


@router.put("/{goal_id}/milestones/{milestone_id}", response_model=GoalMilestoneResponse)
async def update_milestone(
    goal_id: str,
    milestone_id: str,
    payload: GoalMilestoneUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await GoalService.update_milestone(
        db=db, user_id=current_user.id, goal_id=goal_id, milestone_id=milestone_id, payload=payload
    )


@router.delete("/{goal_id}/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    goal_id: str,
    milestone_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await GoalService.delete_milestone(
        db=db, user_id=current_user.id, goal_id=goal_id, milestone_id=milestone_id
    )
