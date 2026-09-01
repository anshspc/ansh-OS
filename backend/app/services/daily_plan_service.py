import uuid
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.calendar_event import CalendarEvent
from app.models.daily_plan import DailyPlan
from app.models.habit import Habit
from app.models.task import Task
from app.models.user import User
from app.schemas.daily_plan import DailyPlanCreate, DailyPlanUpdate, GenerateDailyPlanRequest
from app.services.activity_service import ActivityService


class DailyPlanService:
    @staticmethod
    async def get_daily_plan_by_date(db: AsyncSession, user_id: str, plan_date: str) -> Optional[DailyPlan]:
        stmt = select(DailyPlan).where(DailyPlan.user_id == user_id, DailyPlan.plan_date == plan_date)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def generate_daily_plan(
        db: AsyncSession,
        user_id: str,
        request: GenerateDailyPlanRequest,
    ) -> DailyPlan:
        plan_date = request.date or date.today().isoformat()
        
        # Check user preferences
        stmt_user = select(User).where(User.id == user_id)
        res_user = await db.execute(stmt_user)
        user = res_user.scalar_one()
        prefs = user.preferences or {}
        work_start = request.preferred_start_time or prefs.get("working_hours_start", "09:00")
        work_end = request.preferred_end_time or prefs.get("working_hours_end", "18:00")

        # Fetch candidate tasks
        stmt_tasks = (
            select(Task)
            .where(Task.user_id == user_id, Task.status.in_(["todo", "in_progress", "inbox"]))
            .order_by(
                Task.priority.desc(),
                Task.due_date.asc().nullslast(),
            )
            .limit(10)
        )
        res_tasks = await db.execute(stmt_tasks)
        tasks = list(res_tasks.scalars().all())

        # Fetch today's calendar events
        target_date = date.fromisoformat(plan_date)
        start_dt = datetime.combine(target_date, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(target_date, time.max, tzinfo=timezone.utc)
        stmt_events = (
            select(CalendarEvent)
            .where(
                CalendarEvent.user_id == user_id,
                CalendarEvent.start_time <= end_dt,
                CalendarEvent.end_time >= start_dt,
            )
            .order_by(CalendarEvent.start_time.asc())
        )
        res_events = await db.execute(stmt_events)
        events = list(res_events.scalars().all())

        # Fetch active daily habits
        stmt_habits = select(Habit).where(Habit.user_id == user_id, Habit.is_active == True)
        res_habits = await db.execute(stmt_habits)
        habits = list(res_habits.scalars().all())

        # Construct intelligent schedule time blocks
        time_blocks: List[Dict[str, Any]] = []
        focus_areas: List[str] = []

        start_hour, start_min = map(int, work_start.split(":"))
        end_hour, end_min = map(int, work_end.split(":"))

        current_time = datetime(target_date.year, target_date.month, target_date.day, start_hour, start_min)
        end_time_threshold = datetime(target_date.year, target_date.month, target_date.day, end_hour, end_min)

        # 1. Add morning habits block
        if habits:
            habit_block_end = current_time + timedelta(minutes=30)
            habit_titles = ", ".join([h.title for h in habits[:3]])
            time_blocks.append({
                "id": str(uuid.uuid4())[:8],
                "start_time": current_time.strftime("%H:%M"),
                "end_time": habit_block_end.strftime("%H:%M"),
                "title": f"Morning Routine & Habits ({habit_titles})",
                "type": "habit",
                "task_id": None,
                "completed": False,
            })
            current_time = habit_block_end

        # 2. Schedule Tasks into available slots
        for t in tasks:
            if current_time >= end_time_threshold:
                break
            
            # Check for lunch break around 12:30 - 13:30
            if current_time.hour == 12 and current_time.minute >= 30:
                lunch_end = current_time + timedelta(minutes=45)
                time_blocks.append({
                    "id": str(uuid.uuid4())[:8],
                    "start_time": current_time.strftime("%H:%M"),
                    "end_time": lunch_end.strftime("%H:%M"),
                    "title": "Lunch & Mindful Reset",
                    "type": "break",
                    "task_id": None,
                    "completed": False,
                })
                current_time = lunch_end

            task_duration = min(90, max(25, t.estimated_duration or 45))
            block_end = current_time + timedelta(minutes=task_duration)

            time_blocks.append({
                "id": str(uuid.uuid4())[:8],
                "start_time": current_time.strftime("%H:%M"),
                "end_time": block_end.strftime("%H:%M"),
                "title": t.title,
                "type": "deep_work" if t.priority in ("critical", "high") else "task",
                "task_id": t.id,
                "completed": t.status == "completed",
            })
            focus_areas.append(t.title)
            current_time = block_end + timedelta(minutes=10)  # 10 min transition buffer

        # 3. Add afternoon wrap-up block
        if current_time < end_time_threshold:
            time_blocks.append({
                "id": str(uuid.uuid4())[:8],
                "start_time": current_time.strftime("%H:%M"),
                "end_time": end_time_threshold.strftime("%H:%M"),
                "title": "Daily Reflection, Inbox Zero & Planning Tomorrow",
                "type": "break",
                "task_id": None,
                "completed": False,
            })

        summary = (
            f"Daily schedule prepared with {len(time_blocks)} structured blocks across "
            f"{len([t for t in time_blocks if t['type'] in ('task', 'deep_work')])} focus tasks. "
            f"Optimized for deep work and high priority completion."
        )

        existing_plan = await DailyPlanService.get_daily_plan_by_date(db, user_id, plan_date)
        if existing_plan:
            existing_plan.summary = summary
            existing_plan.time_blocks_json = time_blocks
            existing_plan.focus_areas_json = focus_areas[:5]
            existing_plan.status = "generated"
            plan = existing_plan
        else:
            plan = DailyPlan(
                user_id=user_id,
                plan_date=plan_date,
                summary=summary,
                time_blocks_json=time_blocks,
                focus_areas_json=focus_areas[:5],
                status="generated",
            )
            db.add(plan)

        await db.commit()
        await db.refresh(plan)

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="daily_plan_generated",
            entity_type="daily_plan",
            entity_id=plan.id,
            details={"date": plan_date, "blocks_count": len(time_blocks)},
        )

        return plan

    @staticmethod
    async def update_daily_plan(
        db: AsyncSession,
        user_id: str,
        plan_id: str,
        payload: DailyPlanUpdate,
    ) -> DailyPlan:
        stmt = select(DailyPlan).where(DailyPlan.id == plan_id, DailyPlan.user_id == user_id)
        result = await db.execute(stmt)
        plan = result.scalar_one_or_none()
        if not plan:
            raise NotFoundException(resource="Daily Plan", identifier=plan_id)

        update_data = payload.model_dump(exclude_unset=True)
        if "time_blocks" in update_data and update_data["time_blocks"] is not None:
            plan.time_blocks_json = [b.model_dump() if hasattr(b, "model_dump") else b for b in update_data["time_blocks"]]
        if "focus_areas" in update_data and update_data["focus_areas"] is not None:
            plan.focus_areas_json = update_data["focus_areas"]
        if "summary" in update_data and update_data["summary"] is not None:
            plan.summary = update_data["summary"]
        if "status" in update_data and update_data["status"] is not None:
            plan.status = update_data["status"]

        await db.commit()
        await db.refresh(plan)
        return plan
