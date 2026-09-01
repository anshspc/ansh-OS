from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.services.note_service import NoteService

router = APIRouter()


@router.get("", response_model=List[NoteResponse])
async def get_notes(
    project_id: Optional[str] = None,
    goal_id: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    is_archived: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await NoteService.get_notes(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
        goal_id=goal_id,
        tag=tag,
        search=search,
        is_archived=is_archived,
    )


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await NoteService.create_note(db=db, user_id=current_user.id, payload=payload)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note_by_id(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await NoteService.get_note_by_id(db=db, user_id=current_user.id, note_id=note_id)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await NoteService.update_note(db=db, user_id=current_user.id, note_id=note_id, payload=payload)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await NoteService.delete_note(db=db, user_id=current_user.id, note_id=note_id)
