from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.goal import Goal
from app.models.habit import Habit, HabitLog
from app.models.project import Project
from app.models.task import Task
from app.models.weekly_review import WeeklyReview
from app.schemas.weekly_review import GenerateWeeklyReviewRequest, WeeklyReviewCreate
from app.services.activity_service import ActivityService
from app.services.analytics_service import AnalyticsService


class WeeklyReviewService:
    @staticmethod
    async def get_reviews(db: AsyncSession, user_id: str) -> List[WeeklyReview]:
        stmt = (
            select(WeeklyReview)
            .where(WeeklyReview.user_id == user_id)
            .order_by(WeeklyReview.start_date.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_review_by_id(db: AsyncSession, user_id: str, review_id: str) -> WeeklyReview:
        stmt = select(WeeklyReview).where(WeeklyReview.id == review_id, WeeklyReview.user_id == user_id)
        result = await db.execute(stmt)
        review = result.scalar_one_or_none()
        if not review:
            raise NotFoundException(resource="Weekly Review", identifier=review_id)
        return review

    @staticmethod
    async def generate_weekly_review(
        db: AsyncSession,
        user_id: str,
        request: GenerateWeeklyReviewRequest,
    ) -> WeeklyReview:
        today = date.today()
        start_date_str = request.start_date or (today - timedelta(days=6)).isoformat()
        end_date_str = request.end_date or today.isoformat()

        start_dt = datetime.combine(date.fromisoformat(start_date_str), time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(date.fromisoformat(end_date_str), time.max, tzinfo=timezone.utc)

        # 1. Fetch completed tasks in this window
        stmt_tasks = select(Task).where(Task.user_id == user_id)
        res_tasks = await db.execute(stmt_tasks)
        all_tasks = list(res_tasks.scalars().all())

        completed_tasks = [
            t for t in all_tasks
            if t.completed_at and start_dt <= t.completed_at <= end_dt
        ]
        overdue_tasks = [
            t for t in all_tasks
            if t.due_date and t.due_date < end_dt and t.status != "completed"
        ]

        # 2. Fetch active habits & logs
        stmt_habits = select(Habit).options(selectinload(Habit.logs)).where(Habit.user_id == user_id, Habit.is_active == True)
        res_habits = await db.execute(stmt_habits)
        habits = list(res_habits.scalars().all())

        # 3. Calculate productivity score
        score_data = await AnalyticsService.compute_productivity_score(db, user_id)

        # 4. Generate Wins
        wins: List[str] = []
        if completed_tasks:
            wins.append(f"Completed {len(completed_tasks)} key tasks including '{completed_tasks[0].title}'.")
        for h in habits:
            if h.streak_count >= 5:
                wins.append(f"Maintained an exceptional {h.streak_count}-day streak on '{h.title}'.")
        if not wins:
            wins.append("Maintained consistent baseline activity and prepared strategic roadmap.")

        # 5. Identify Bottlenecks
        bottlenecks: List[str] = []
        if overdue_tasks:
            bottlenecks.append(f"{len(overdue_tasks)} task(s) slipped past deadline (e.g. '{overdue_tasks[0].title}').")
        low_habits = [h for h in habits if h.streak_count < 2]
        if low_habits:
            bottlenecks.append(f"Consistency dip detected in '{low_habits[0].title}'.")
        if not bottlenecks:
            bottlenecks.append("No critical friction points detected this cycle. Workflow efficiency was high.")

        # 6. Synthesize Actionable Recommendations
        recommendations: List[str] = [
            "Time-box your highest leverage task during the morning 09:00 - 11:00 deep work block.",
            "Review your goal milestones and break any tasks exceeding 90 minutes into subtasks.",
            "Maintain your habit check-ins daily to keep compounding long-term progress.",
        ]

        summary = (
            f"Weekly Performance Review ({start_date_str} to {end_date_str}): "
            f"Achieved a {score_data.grade}-tier productivity score of {score_data.total_score}/100. "
            f"{len(completed_tasks)} tasks delivered successfully."
        )

        review = WeeklyReview(
            user_id=user_id,
            start_date=start_date_str,
            end_date=end_date_str,
            summary=summary,
            wins_json=wins,
            bottlenecks_json=bottlenecks,
            recommendations_json=recommendations,
            productivity_score=score_data.total_score,
            stats_json={
                "completed_tasks_count": len(completed_tasks),
                "overdue_tasks_count": len(overdue_tasks),
                "habits_tracked": len(habits),
                "score_breakdown": score_data.breakdown.model_dump(),
            },
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="weekly_review_generated",
            entity_type="weekly_review",
            entity_id=review.id,
            details={"start_date": start_date_str, "score": score_data.total_score},
        )

        return review
