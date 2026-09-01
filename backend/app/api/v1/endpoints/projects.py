from typing import Any, List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.project import (
    MilestoneCreate, MilestoneResponse, MilestoneUpdate, ProjectCreate, ProjectResponse, ProjectUpdate
)
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ProjectService.get_projects(db=db, user_id=current_user.id, status=status)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ProjectService.create_project(db=db, user_id=current_user.id, payload=payload)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ProjectService.get_project_by_id(db=db, user_id=current_user.id, project_id=project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ProjectService.update_project(db=db, user_id=current_user.id, project_id=project_id, payload=payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await ProjectService.delete_project(db=db, user_id=current_user.id, project_id=project_id)


@router.post("/{project_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def add_milestone(
    project_id: str,
    payload: MilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ProjectService.add_milestone(db=db, user_id=current_user.id, project_id=project_id, payload=payload)


@router.put("/{project_id}/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    project_id: str,
    milestone_id: str,
    payload: MilestoneUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ProjectService.update_milestone(
        db=db, user_id=current_user.id, project_id=project_id, milestone_id=milestone_id, payload=payload
    )


@router.delete("/{project_id}/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    project_id: str,
    milestone_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await ProjectService.delete_milestone(
        db=db, user_id=current_user.id, project_id=project_id, milestone_id=milestone_id
    )
