from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.project import Milestone, Project
from app.models.task import Task
from app.schemas.project import MilestoneCreate, MilestoneUpdate, ProjectCreate, ProjectUpdate
from app.services.activity_service import ActivityService


class ProjectService:
    @staticmethod
    async def get_projects(
        db: AsyncSession,
        user_id: str,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(Project)
            .options(selectinload(Project.milestones), selectinload(Project.tasks))
            .where(Project.user_id == user_id)
        )
        if status:
            stmt = stmt.where(Project.status == status)
        stmt = stmt.order_by(Project.created_at.desc())

        result = await db.execute(stmt)
        projects = list(result.scalars().all())

        response_list = []
        for p in projects:
            total_tasks = len(p.tasks)
            completed_tasks = sum(1 for t in p.tasks if t.status == "completed")
            calculated_progress = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else p.progress

            response_list.append({
                "id": p.id,
                "user_id": p.user_id,
                "goal_id": p.goal_id,
                "title": p.title,
                "description": p.description,
                "status": p.status,
                "color": p.color,
                "icon": p.icon,
                "start_date": p.start_date,
                "target_date": p.target_date,
                "progress": round(calculated_progress, 1),
                "tags": p.tags or [],
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "milestones": p.milestones,
                "tasks_count": total_tasks,
                "completed_tasks_count": completed_tasks,
            })
        return response_list

    @staticmethod
    async def get_project_by_id(db: AsyncSession, user_id: str, project_id: str) -> Dict[str, Any]:
        stmt = (
            select(Project)
            .options(selectinload(Project.milestones), selectinload(Project.tasks))
            .where(Project.id == project_id, Project.user_id == user_id)
        )
        result = await db.execute(stmt)
        p = result.scalar_one_or_none()
        if not p:
            raise NotFoundException(resource="Project", identifier=project_id)

        total_tasks = len(p.tasks)
        completed_tasks = sum(1 for t in p.tasks if t.status == "completed")
        calculated_progress = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else p.progress

        return {
            "id": p.id,
            "user_id": p.user_id,
            "goal_id": p.goal_id,
            "title": p.title,
            "description": p.description,
            "status": p.status,
            "color": p.color,
            "icon": p.icon,
            "start_date": p.start_date,
            "target_date": p.target_date,
            "progress": round(calculated_progress, 1),
            "tags": p.tags or [],
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "milestones": p.milestones,
            "tasks_count": total_tasks,
            "completed_tasks_count": completed_tasks,
        }

    @staticmethod
    async def create_project(db: AsyncSession, user_id: str, payload: ProjectCreate) -> Dict[str, Any]:
        project = Project(
            user_id=user_id,
            goal_id=payload.goal_id,
            title=payload.title,
            description=payload.description,
            status=payload.status,
            color=payload.color,
            icon=payload.icon,
            start_date=payload.start_date,
            target_date=payload.target_date,
            tags=payload.tags,
        )
        db.add(project)
        await db.flush()

        if payload.milestones:
            for idx, ms in enumerate(payload.milestones):
                milestone = Milestone(
                    project_id=project.id,
                    title=ms.title,
                    description=ms.description,
                    due_date=ms.due_date,
                    position=idx,
                )
                db.add(milestone)

        await db.commit()
        await db.refresh(project)

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="project_created",
            entity_type="project",
            entity_id=project.id,
            details={"title": project.title, "status": project.status},
        )

        return await ProjectService.get_project_by_id(db, user_id, project.id)

    @staticmethod
    async def update_project(db: AsyncSession, user_id: str, project_id: str, payload: ProjectUpdate) -> Dict[str, Any]:
        stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            raise NotFoundException(resource="Project", identifier=project_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        await db.commit()
        return await ProjectService.get_project_by_id(db, user_id, project.id)

    @staticmethod
    async def delete_project(db: AsyncSession, user_id: str, project_id: str) -> None:
        stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            raise NotFoundException(resource="Project", identifier=project_id)
        
        project_title = project.title
        await db.delete(project)
        await db.commit()

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="project_deleted",
            entity_type="project",
            entity_id=project_id,
            details={"title": project_title},
        )

    @staticmethod
    async def add_milestone(db: AsyncSession, user_id: str, project_id: str, payload: MilestoneCreate) -> Milestone:
        await ProjectService.get_project_by_id(db, user_id, project_id)
        milestone = Milestone(
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            due_date=payload.due_date,
            position=payload.position,
        )
        db.add(milestone)
        await db.commit()
        await db.refresh(milestone)
        return milestone

    @staticmethod
    async def update_milestone(db: AsyncSession, user_id: str, project_id: str, milestone_id: str, payload: MilestoneUpdate) -> Milestone:
        await ProjectService.get_project_by_id(db, user_id, project_id)
        stmt = select(Milestone).where(Milestone.id == milestone_id, Milestone.project_id == project_id)
        result = await db.execute(stmt)
        milestone = result.scalar_one_or_none()
        if not milestone:
            raise NotFoundException(resource="Milestone", identifier=milestone_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(milestone, field, value)

        await db.commit()
        await db.refresh(milestone)
        return milestone

    @staticmethod
    async def delete_milestone(db: AsyncSession, user_id: str, project_id: str, milestone_id: str) -> None:
        await ProjectService.get_project_by_id(db, user_id, project_id)
        stmt = select(Milestone).where(Milestone.id == milestone_id, Milestone.project_id == project_id)
        result = await db.execute(stmt)
        milestone = result.scalar_one_or_none()
        if not milestone:
            raise NotFoundException(resource="Milestone", identifier=milestone_id)
        await db.delete(milestone)
        await db.commit()
