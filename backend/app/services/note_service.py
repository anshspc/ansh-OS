from typing import Any, Dict, List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.activity_service import ActivityService


class NoteService:
    @staticmethod
    async def get_notes(
        db: AsyncSession,
        user_id: str,
        project_id: Optional[str] = None,
        goal_id: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        is_archived: bool = False,
    ) -> List[Note]:
        stmt = (
            select(Note)
            .where(Note.user_id == user_id, Note.is_archived == is_archived)
        )
        if project_id:
            stmt = stmt.where(Note.project_id == project_id)
        if goal_id:
            stmt = stmt.where(Note.goal_id == goal_id)
        if search:
            stmt = stmt.where(
                or_(
                    Note.title.ilike(f"%{search}%"),
                    Note.content.ilike(f"%{search}%"),
                )
            )
        stmt = stmt.order_by(Note.is_pinned.desc(), Note.updated_at.desc())

        result = await db.execute(stmt)
        notes = list(result.scalars().all())

        if tag:
            notes = [n for n in notes if tag in (n.tags or [])]

        return notes

    @staticmethod
    async def get_note_by_id(db: AsyncSession, user_id: str, note_id: str) -> Note:
        stmt = select(Note).where(Note.id == note_id, Note.user_id == user_id)
        result = await db.execute(stmt)
        note = result.scalar_one_or_none()
        if not note:
            raise NotFoundException(resource="Note", identifier=note_id)
        return note

    @staticmethod
    async def create_note(db: AsyncSession, user_id: str, payload: NoteCreate) -> Note:
        note = Note(
            user_id=user_id,
            project_id=payload.project_id,
            goal_id=payload.goal_id,
            title=payload.title,
            content=payload.content,
            tags=payload.tags,
            is_pinned=payload.is_pinned,
        )
        db.add(note)
        await db.commit()
        await db.refresh(note)

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="note_created",
            entity_type="note",
            entity_id=note.id,
            details={"title": note.title},
        )

        return note

    @staticmethod
    async def update_note(db: AsyncSession, user_id: str, note_id: str, payload: NoteUpdate) -> Note:
        note = await NoteService.get_note_by_id(db, user_id, note_id)
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(note, field, value)

        await db.commit()
        await db.refresh(note)
        return note

    @staticmethod
    async def delete_note(db: AsyncSession, user_id: str, note_id: str) -> None:
        note = await NoteService.get_note_by_id(db, user_id, note_id)
        note_title = note.title
        await db.delete(note)
        await db.commit()

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="note_deleted",
            entity_type="note",
            entity_id=note_id,
            details={"title": note_title},
        )
