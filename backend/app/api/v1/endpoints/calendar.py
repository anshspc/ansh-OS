from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.calendar_event import (
    CalendarEventCreate, CalendarEventResponse, CalendarEventUpdate
)
from app.services.calendar_service import CalendarService

router = APIRouter()


@router.get("/events", response_model=List[CalendarEventResponse])
async def get_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await CalendarService.get_events(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        event_type=event_type,
    )


@router.post("/events", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: CalendarEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await CalendarService.create_event(db=db, user_id=current_user.id, payload=payload)


@router.get("/events/{event_id}", response_model=CalendarEventResponse)
async def get_event_by_id(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await CalendarService.get_event_by_id(db=db, user_id=current_user.id, event_id=event_id)


@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: str,
    payload: CalendarEventUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await CalendarService.update_event(
        db=db, user_id=current_user.id, event_id=event_id, payload=payload
    )


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await CalendarService.delete_event(db=db, user_id=current_user.id, event_id=event_id)
