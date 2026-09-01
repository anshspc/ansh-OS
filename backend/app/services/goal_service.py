from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.goal import Goal, GoalMilestone
from app.models.project import Project
from app.models.task import Task
from app.schemas.goal import GoalCreate, GoalMilestoneCreate, GoalMilestoneUpdate, GoalUpdate
from app.services.activity_service import ActivityService


class GoalService:
    @staticmethod
    async def get_goals(
        db: AsyncSession,
        user_id: str,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(Goal)
            .options(
                selectinload(Goal.milestones),
                selectinload(Goal.projects),
                selectinload(Goal.tasks),
            )
            .where(Goal.user_id == user_id)
        )
        if category:
            stmt = stmt.where(Goal.category == category)
        if status:
            stmt = stmt.where(Goal.status == status)
        stmt = stmt.order_by(Goal.created_at.desc())

        result = await db.execute(stmt)
        goals = list(result.scalars().all())

        response_list = []
        for g in goals:
            total_milestones = len(g.milestones)
            completed_milestones = sum(1 for m in g.milestones if m.is_completed)
            if total_milestones > 0:
                calc_progress = round(completed_milestones / total_milestones * 100.0, 1)
            else:
                calc_progress = g.progress

            response_list.append({
                "id": g.id,
                "user_id": g.user_id,
                "title": g.title,
                "description": g.description,
                "category": g.category,
                "target_date": g.target_date,
                "progress": calc_progress,
                "status": g.status,
                "color": g.color,
                "icon": g.icon,
                "metrics": g.metrics or {},
                "created_at": g.created_at,
                "updated_at": g.updated_at,
                "milestones": g.milestones,
                "linked_projects_count": len(g.projects),
                "linked_tasks_count": len(g.tasks),
            })
        return response_list

    @staticmethod
    async def get_goal_by_id(db: AsyncSession, user_id: str, goal_id: str) -> Dict[str, Any]:
        stmt = (
            select(Goal)
            .options(
                selectinload(Goal.milestones),
                selectinload(Goal.projects),
                selectinload(Goal.tasks),
            )
            .where(Goal.id == goal_id, Goal.user_id == user_id)
        )
        result = await db.execute(stmt)
        g = result.scalar_one_or_none()
        if not g:
            raise NotFoundException(resource="Goal", identifier=goal_id)

        total_milestones = len(g.milestones)
        completed_milestones = sum(1 for m in g.milestones if m.is_completed)
        if total_milestones > 0:
            calc_progress = round(completed_milestones / total_milestones * 100.0, 1)
        else:
            calc_progress = g.progress

        return {
            "id": g.id,
            "user_id": g.user_id,
            "title": g.title,
            "description": g.description,
            "category": g.category,
            "target_date": g.target_date,
            "progress": calc_progress,
            "status": g.status,
            "color": g.color,
            "icon": g.icon,
            "metrics": g.metrics or {},
            "created_at": g.created_at,
            "updated_at": g.updated_at,
            "milestones": g.milestones,
            "linked_projects_count": len(g.projects),
            "linked_tasks_count": len(g.tasks),
        }

    @staticmethod
    async def create_goal(db: AsyncSession, user_id: str, payload: GoalCreate) -> Dict[str, Any]:
        goal = Goal(
            user_id=user_id,
            title=payload.title,
            description=payload.description,
            category=payload.category,
            target_date=payload.target_date,
            status=payload.status,
            color=payload.color,
            icon=payload.icon,
            metrics=payload.metrics,
        )
        db.add(goal)
        await db.flush()

        if payload.milestones:
            for idx, ms in enumerate(payload.milestones):
                milestone = GoalMilestone(
                    goal_id=goal.id,
                    title=ms.title,
                    due_date=ms.due_date,
                    position=idx,
                )
                db.add(milestone)

        await db.commit()
        await db.refresh(goal)

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="goal_created",
            entity_type="goal",
            entity_id=goal.id,
            details={"title": goal.title, "category": goal.category},
        )

        return await GoalService.get_goal_by_id(db, user_id, goal.id)

    @staticmethod
    async def update_goal(db: AsyncSession, user_id: str, goal_id: str, payload: GoalUpdate) -> Dict[str, Any]:
        stmt = select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        result = await db.execute(stmt)
        goal = result.scalar_one_or_none()
        if not goal:
            raise NotFoundException(resource="Goal", identifier=goal_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)

        await db.commit()
        return await GoalService.get_goal_by_id(db, user_id, goal.id)

    @staticmethod
    async def delete_goal(db: AsyncSession, user_id: str, goal_id: str) -> None:
        stmt = select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        result = await db.execute(stmt)
        goal = result.scalar_one_or_none()
        if not goal:
            raise NotFoundException(resource="Goal", identifier=goal_id)

        goal_title = goal.title
        await db.delete(goal)
        await db.commit()

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="goal_deleted",
            entity_type="goal",
            entity_id=goal_id,
            details={"title": goal_title},
        )

    @staticmethod
    async def add_milestone(db: AsyncSession, user_id: str, goal_id: str, payload: GoalMilestoneCreate) -> GoalMilestone:
        await GoalService.get_goal_by_id(db, user_id, goal_id)
        milestone = GoalMilestone(
            goal_id=goal_id,
            title=payload.title,
            due_date=payload.due_date,
            position=payload.position,
        )
        db.add(milestone)
        await db.commit()
        await db.refresh(milestone)
        return milestone

    @staticmethod
    async def update_milestone(db: AsyncSession, user_id: str, goal_id: str, milestone_id: str, payload: GoalMilestoneUpdate) -> GoalMilestone:
        await GoalService.get_goal_by_id(db, user_id, goal_id)
        stmt = select(GoalMilestone).where(GoalMilestone.id == milestone_id, GoalMilestone.goal_id == goal_id)
        result = await db.execute(stmt)
        milestone = result.scalar_one_or_none()
        if not milestone:
            raise NotFoundException(resource="Goal Milestone", identifier=milestone_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(milestone, field, value)

        await db.commit()
        await db.refresh(milestone)
        return milestone

    @staticmethod
    async def delete_milestone(db: AsyncSession, user_id: str, goal_id: str, milestone_id: str) -> None:
        await GoalService.get_goal_by_id(db, user_id, goal_id)
        stmt = select(GoalMilestone).where(GoalMilestone.id == milestone_id, GoalMilestone.goal_id == goal_id)
        result = await db.execute(stmt)
        milestone = result.scalar_one_or_none()
        if not milestone:
            raise NotFoundException(resource="Goal Milestone", identifier=milestone_id)
        await db.delete(milestone)
        await db.commit()
