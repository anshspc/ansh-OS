from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.calendar_event import CalendarEvent
from app.models.task import Task
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate
from app.services.activity_service import ActivityService


class CalendarService:
    @staticmethod
    async def get_events(
        db: AsyncSession,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
    ) -> List[CalendarEvent]:
        stmt = select(CalendarEvent).where(CalendarEvent.user_id == user_id)

        if start_date:
            stmt = stmt.where(CalendarEvent.end_time >= start_date)
        if end_date:
            stmt = stmt.where(CalendarEvent.start_time <= end_date)
        if event_type:
            stmt = stmt.where(CalendarEvent.event_type == event_type)

        stmt = stmt.order_by(CalendarEvent.start_time.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_event_by_id(db: AsyncSession, user_id: str, event_id: str) -> CalendarEvent:
        stmt = select(CalendarEvent).where(CalendarEvent.id == event_id, CalendarEvent.user_id == user_id)
        result = await db.execute(stmt)
        event = result.scalar_one_or_none()
        if not event:
            raise NotFoundException(resource="Calendar Event", identifier=event_id)
        return event

    @staticmethod
    async def create_event(db: AsyncSession, user_id: str, payload: CalendarEventCreate) -> CalendarEvent:
        event = CalendarEvent(
            user_id=user_id,
            title=payload.title,
            description=payload.description,
            start_time=payload.start_time,
            end_time=payload.end_time,
            is_all_day=payload.is_all_day,
            event_type=payload.event_type,
            color=payload.color,
            location=payload.location,
            recurrence=payload.recurrence,
            metadata_json=payload.metadata_json,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="calendar_event_created",
            entity_type="calendar_event",
            entity_id=event.id,
            details={"title": event.title, "start": str(event.start_time)},
        )

        return event

    @staticmethod
    async def update_event(db: AsyncSession, user_id: str, event_id: str, payload: CalendarEventUpdate) -> CalendarEvent:
        event = await CalendarService.get_event_by_id(db, user_id, event_id)
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(event, field, value)

        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def delete_event(db: AsyncSession, user_id: str, event_id: str) -> None:
        event = await CalendarService.get_event_by_id(db, user_id, event_id)
        await db.delete(event)
        await db.commit()
