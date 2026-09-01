from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import SubtaskCreate, SubtaskResponse, SubtaskUpdate, TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    project_id: Optional[str] = None,
    goal_id: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await TaskService.get_tasks(
        db=db,
        user_id=current_user.id,
        status=status,
        priority=priority,
        project_id=project_id,
        goal_id=goal_id,
        tag=tag,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await TaskService.create_task(db=db, user_id=current_user.id, payload=payload)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await TaskService.get_task_by_id(db=db, user_id=current_user.id, task_id=task_id)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await TaskService.update_task(db=db, user_id=current_user.id, task_id=task_id, payload=payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await TaskService.delete_task(db=db, user_id=current_user.id, task_id=task_id)


@router.post("/{task_id}/subtasks", response_model=SubtaskResponse, status_code=status.HTTP_201_CREATED)
async def add_subtask(
    task_id: str,
    payload: SubtaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await TaskService.add_subtask(db=db, user_id=current_user.id, task_id=task_id, payload=payload)


@router.put("/{task_id}/subtasks/{subtask_id}", response_model=SubtaskResponse)
async def update_subtask(
    task_id: str,
    subtask_id: str,
    payload: SubtaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await TaskService.update_subtask(db=db, user_id=current_user.id, task_id=task_id, subtask_id=subtask_id, payload=payload)


@router.delete("/{task_id}/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtask(
    task_id: str,
    subtask_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await TaskService.delete_subtask(db=db, user_id=current_user.id, task_id=task_id, subtask_id=subtask_id)
