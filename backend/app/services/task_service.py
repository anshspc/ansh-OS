from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.task import Subtask, Task
from app.schemas.task import SubtaskCreate, SubtaskUpdate, TaskCreate, TaskUpdate
from app.services.activity_service import ActivityService


class TaskService:
    @staticmethod
    async def get_tasks(
        db: AsyncSession,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        project_id: Optional[str] = None,
        goal_id: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Task]:
        stmt = (
            select(Task)
            .options(selectinload(Task.subtasks))
            .where(Task.user_id == user_id)
        )
        
        if status:
            stmt = stmt.where(Task.status == status)
        if priority:
            stmt = stmt.where(Task.priority == priority)
        if project_id:
            stmt = stmt.where(Task.project_id == project_id)
        if goal_id:
            stmt = stmt.where(Task.goal_id == goal_id)
        if search:
            stmt = stmt.where(
                or_(
                    Task.title.ilike(f"%{search}%"),
                    Task.description.ilike(f"%{search}%"),
                )
            )

        stmt = stmt.order_by(Task.position.asc(), Task.due_date.asc().nullslast(), Task.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await db.execute(stmt)
        tasks = list(result.scalars().all())
        
        if tag:
            tasks = [t for t in tasks if tag in (t.tags or [])]
            
        return tasks

    @staticmethod
    async def get_task_by_id(db: AsyncSession, user_id: str, task_id: str) -> Task:
        stmt = (
            select(Task)
            .options(selectinload(Task.subtasks))
            .where(Task.id == task_id, Task.user_id == user_id)
        )
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundException(resource="Task", identifier=task_id)
        return task

    @staticmethod
    async def create_task(db: AsyncSession, user_id: str, payload: TaskCreate) -> Task:
        completed_at = datetime.now(timezone.utc) if payload.status == "completed" else None
        
        task = Task(
            user_id=user_id,
            title=payload.title,
            description=payload.description,
            project_id=payload.project_id,
            goal_id=payload.goal_id,
            status=payload.status,
            priority=payload.priority,
            due_date=payload.due_date,
            estimated_duration=payload.estimated_duration,
            tags=payload.tags,
            recurring=payload.recurring,
            recurrence_rule=payload.recurrence_rule,
            completed_at=completed_at,
        )
        db.add(task)
        await db.flush()

        if payload.subtasks:
            for idx, st in enumerate(payload.subtasks):
                subtask = Subtask(
                    task_id=task.id,
                    title=st.title,
                    is_completed=st.is_completed,
                    position=idx,
                )
                db.add(subtask)

        await db.commit()
        await db.refresh(task)
        
        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="task_created",
            entity_type="task",
            entity_id=task.id,
            details={"title": task.title, "priority": task.priority, "status": task.status},
        )
        
        return await TaskService.get_task_by_id(db, user_id, task.id)

    @staticmethod
    async def update_task(db: AsyncSession, user_id: str, task_id: str, payload: TaskUpdate) -> Task:
        task = await TaskService.get_task_by_id(db, user_id, task_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == "completed" and task.status != "completed":
                task.completed_at = datetime.now(timezone.utc)
                await ActivityService.log_activity(
                    db=db,
                    user_id=user_id,
                    action="task_completed",
                    entity_type="task",
                    entity_id=task.id,
                    details={"title": task.title},
                )
            elif new_status != "completed":
                task.completed_at = None

        for field, value in update_data.items():
            setattr(task, field, value)

        await db.commit()
        await db.refresh(task)
        return await TaskService.get_task_by_id(db, user_id, task.id)

    @staticmethod
    async def delete_task(db: AsyncSession, user_id: str, task_id: str) -> None:
        task = await TaskService.get_task_by_id(db, user_id, task_id)
        task_title = task.title
        await db.delete(task)
        await db.commit()
        
        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="task_deleted",
            entity_type="task",
            entity_id=task_id,
            details={"title": task_title},
        )

    @staticmethod
    async def add_subtask(db: AsyncSession, user_id: str, task_id: str, payload: SubtaskCreate) -> Subtask:
        task = await TaskService.get_task_by_id(db, user_id, task_id)
        subtask = Subtask(
            task_id=task.id,
            title=payload.title,
            is_completed=payload.is_completed,
            position=payload.position,
        )
        db.add(subtask)
        await db.commit()
        await db.refresh(subtask)
        return subtask

    @staticmethod
    async def update_subtask(db: AsyncSession, user_id: str, task_id: str, subtask_id: str, payload: SubtaskUpdate) -> Subtask:
        await TaskService.get_task_by_id(db, user_id, task_id)
        stmt = select(Subtask).where(Subtask.id == subtask_id, Subtask.task_id == task_id)
        result = await db.execute(stmt)
        subtask = result.scalar_one_or_none()
        if not subtask:
            raise NotFoundException(resource="Subtask", identifier=subtask_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(subtask, field, value)

        await db.commit()
        await db.refresh(subtask)
        return subtask

    @staticmethod
    async def delete_subtask(db: AsyncSession, user_id: str, task_id: str, subtask_id: str) -> None:
        await TaskService.get_task_by_id(db, user_id, task_id)
        stmt = select(Subtask).where(Subtask.id == subtask_id, Subtask.task_id == task_id)
        result = await db.execute(stmt)
        subtask = result.scalar_one_or_none()
        if not subtask:
            raise NotFoundException(resource="Subtask", identifier=subtask_id)
        await db.delete(subtask)
        await db.commit()
