from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.habit import Habit, HabitLog
from app.schemas.habit import HabitCreate, HabitLogCreate, HabitUpdate
from app.services.activity_service import ActivityService


class HabitService:
    @staticmethod
    def _calculate_streaks(logs: List[HabitLog]) -> tuple[int, int]:
        """Calculate current streak and best streak from sorted date logs."""
        if not logs:
            return 0, 0

        completed_dates = set(log.logged_date for log in logs if log.completed)
        if not completed_dates:
            return 0, 0

        today = date.today()
        today_str = today.isoformat()
        yesterday_str = (today - timedelta(days=1)).isoformat()

        # Check current streak starting from today or yesterday
        current_streak = 0
        curr = today
        if today_str not in completed_dates:
            curr = today - timedelta(days=1)

        while curr.isoformat() in completed_dates:
            current_streak += 1
            curr -= timedelta(days=1)

        # Calculate all-time best streak
        sorted_dates = sorted(list(completed_dates))
        best_streak = 0
        current_run = 0
        prev_d = None

        for d_str in sorted_dates:
            d = date.fromisoformat(d_str)
            if prev_d is None or (d - prev_d).days == 1:
                current_run += 1
            elif (d - prev_d).days > 1:
                current_run = 1
            prev_d = d
            if current_run > best_streak:
                best_streak = current_run

        return current_streak, max(best_streak, current_streak)

    @staticmethod
    async def get_habits(db: AsyncSession, user_id: str) -> List[Dict[str, Any]]:
        stmt = (
            select(Habit)
            .options(selectinload(Habit.logs))
            .where(Habit.user_id == user_id, Habit.is_active == True)
            .order_by(Habit.created_at.asc())
        )
        result = await db.execute(stmt)
        habits = list(result.scalars().all())

        today_str = date.today().isoformat()
        thirty_days_ago_str = (date.today() - timedelta(days=30)).isoformat()

        response = []
        for h in habits:
            today_done = any(l.logged_date == today_str and l.completed for l in h.logs)
            recent_logs = [l for l in h.logs if l.logged_date >= thirty_days_ago_str]
            completed_30d = sum(1 for l in recent_logs if l.completed)
            completion_rate = round((completed_30d / 30.0) * 100.0, 1)

            curr_streak, best_streak = HabitService._calculate_streaks(h.logs)
            if curr_streak != h.streak_count or best_streak > h.best_streak:
                h.streak_count = curr_streak
                h.best_streak = max(h.best_streak, best_streak)

            response.append({
                "id": h.id,
                "user_id": h.user_id,
                "goal_id": h.goal_id,
                "title": h.title,
                "description": h.description,
                "frequency": h.frequency,
                "target_days": h.target_days or [0, 1, 2, 3, 4, 5, 6],
                "reminder_time": h.reminder_time,
                "streak_count": h.streak_count,
                "best_streak": h.best_streak,
                "color": h.color,
                "icon": h.icon,
                "is_active": h.is_active,
                "created_at": h.created_at,
                "updated_at": h.updated_at,
                "today_completed": today_done,
                "completion_rate_30d": completion_rate,
                "recent_logs": h.logs[:30],
            })
        await db.commit()
        return response

    @staticmethod
    async def get_habit_by_id(db: AsyncSession, user_id: str, habit_id: str) -> Dict[str, Any]:
        stmt = (
            select(Habit)
            .options(selectinload(Habit.logs))
            .where(Habit.id == habit_id, Habit.user_id == user_id)
        )
        result = await db.execute(stmt)
        h = result.scalar_one_or_none()
        if not h:
            raise NotFoundException(resource="Habit", identifier=habit_id)

        today_str = date.today().isoformat()
        thirty_days_ago_str = (date.today() - timedelta(days=30)).isoformat()
        today_done = any(l.logged_date == today_str and l.completed for l in h.logs)
        recent_logs = [l for l in h.logs if l.logged_date >= thirty_days_ago_str]
        completed_30d = sum(1 for l in recent_logs if l.completed)
        completion_rate = round((completed_30d / 30.0) * 100.0, 1)

        curr_streak, best_streak = HabitService._calculate_streaks(h.logs)

        return {
            "id": h.id,
            "user_id": h.user_id,
            "goal_id": h.goal_id,
            "title": h.title,
            "description": h.description,
            "frequency": h.frequency,
            "target_days": h.target_days or [0, 1, 2, 3, 4, 5, 6],
            "reminder_time": h.reminder_time,
            "streak_count": curr_streak,
            "best_streak": max(h.best_streak, best_streak),
            "color": h.color,
            "icon": h.icon,
            "is_active": h.is_active,
            "created_at": h.created_at,
            "updated_at": h.updated_at,
            "today_completed": today_done,
            "completion_rate_30d": completion_rate,
            "recent_logs": h.logs,
        }

    @staticmethod
    async def create_habit(db: AsyncSession, user_id: str, payload: HabitCreate) -> Dict[str, Any]:
        habit = Habit(
            user_id=user_id,
            goal_id=payload.goal_id,
            title=payload.title,
            description=payload.description,
            frequency=payload.frequency,
            target_days=payload.target_days,
            reminder_time=payload.reminder_time,
            color=payload.color,
            icon=payload.icon,
        )
        db.add(habit)
        await db.commit()
        await db.refresh(habit)

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="habit_created",
            entity_type="habit",
            entity_id=habit.id,
            details={"title": habit.title},
        )

        return await HabitService.get_habit_by_id(db, user_id, habit.id)

    @staticmethod
    async def update_habit(db: AsyncSession, user_id: str, habit_id: str, payload: HabitUpdate) -> Dict[str, Any]:
        stmt = select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
        result = await db.execute(stmt)
        habit = result.scalar_one_or_none()
        if not habit:
            raise NotFoundException(resource="Habit", identifier=habit_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(habit, field, value)

        await db.commit()
        return await HabitService.get_habit_by_id(db, user_id, habit.id)

    @staticmethod
    async def log_habit(db: AsyncSession, user_id: str, habit_id: str, payload: HabitLogCreate) -> Dict[str, Any]:
        stmt = select(Habit).options(selectinload(Habit.logs)).where(Habit.id == habit_id, Habit.user_id == user_id)
        result = await db.execute(stmt)
        habit = result.scalar_one_or_none()
        if not habit:
            raise NotFoundException(resource="Habit", identifier=habit_id)

        stmt_log = select(HabitLog).where(HabitLog.habit_id == habit_id, HabitLog.logged_date == payload.logged_date)
        res_log = await db.execute(stmt_log)
        existing_log = res_log.scalar_one_or_none()

        if existing_log:
            existing_log.completed = payload.completed
            existing_log.value = payload.value
            existing_log.notes = payload.notes
        else:
            new_log = HabitLog(
                habit_id=habit_id,
                user_id=user_id,
                logged_date=payload.logged_date,
                completed=payload.completed,
                value=payload.value,
                notes=payload.notes,
            )
            db.add(new_log)
            habit.logs.append(new_log)

        await db.flush()
        curr_streak, best_streak = HabitService._calculate_streaks(habit.logs)
        habit.streak_count = curr_streak
        habit.best_streak = max(habit.best_streak, best_streak)

        await db.commit()

        if payload.completed:
            await ActivityService.log_activity(
                db=db,
                user_id=user_id,
                action="habit_completed",
                entity_type="habit",
                entity_id=habit.id,
                details={"title": habit.title, "date": payload.logged_date, "streak": habit.streak_count},
            )

        return await HabitService.get_habit_by_id(db, user_id, habit.id)

    @staticmethod
    async def delete_habit(db: AsyncSession, user_id: str, habit_id: str) -> None:
        stmt = select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
        result = await db.execute(stmt)
        habit = result.scalar_one_or_none()
        if not habit:
            raise NotFoundException(resource="Habit", identifier=habit_id)
        await db.delete(habit)
        await db.commit()

    @staticmethod
    async def get_heatmap_data(db: AsyncSession, user_id: str, days: int = 365) -> Dict[str, int]:
        """Aggregate completion counts across all habits per day for the last N days."""
        start_date_str = (date.today() - timedelta(days=days)).isoformat()
        stmt = (
            select(HabitLog.logged_date, func.count(HabitLog.id))
            .where(
                HabitLog.user_id == user_id,
                HabitLog.completed == True,
                HabitLog.logged_date >= start_date_str,
            )
            .group_by(HabitLog.logged_date)
        )
        result = await db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
