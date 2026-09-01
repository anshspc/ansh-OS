from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.orchestrator import AIOrchestrator
from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.models.ai_conversation import AIConversation, AIMessage
from app.models.user import User
from app.schemas.ai import (
    AIChatMessageRequest, AIChatResponse, AIConversationResponse, AIMemoryCreate,
    AIMemoryResponse, AIMemoryUpdate, AIMessageResponse, ToolExecutionConfirmationRequest
)
from app.services.ai_memory_service import AIMemoryService

router = APIRouter()


@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(
    payload: AIChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await AIOrchestrator.process_chat(db=db, user=current_user, payload=payload)


@router.get("/conversations", response_model=List[AIConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    stmt = (
        select(AIConversation)
        .where(AIConversation.user_id == current_user.id)
        .order_by(AIConversation.pinned.desc(), AIConversation.updated_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/conversations/{conversation_id}/messages", response_model=List[AIMessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    stmt = select(AIConversation).where(AIConversation.id == conversation_id, AIConversation.user_id == current_user.id)
    res = await db.execute(stmt)
    if not res.scalar_one_or_none():
        raise NotFoundException(resource="Conversation", identifier=conversation_id)

    stmt_msgs = (
        select(AIMessage)
        .where(AIMessage.conversation_id == conversation_id)
        .order_by(AIMessage.created_at.asc())
    )
    res_msgs = await db.execute(stmt_msgs)
    return list(res_msgs.scalars().all())


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    stmt = select(AIConversation).where(AIConversation.id == conversation_id, AIConversation.user_id == current_user.id)
    res = await db.execute(stmt)
    conv = res.scalar_one_or_none()
    if not conv:
        raise NotFoundException(resource="Conversation", identifier=conversation_id)
    await db.delete(conv)
    await db.commit()


# Memories Endpoints
@router.get("/memories", response_model=List[AIMemoryResponse])
async def get_memories(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await AIMemoryService.get_memories(db=db, user_id=current_user.id, category=category)


@router.post("/memories", response_model=AIMemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    payload: AIMemoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await AIMemoryService.create_memory(db=db, user_id=current_user.id, payload=payload)


@router.put("/memories/{memory_id}", response_model=AIMemoryResponse)
async def update_memory(
    memory_id: str,
    payload: AIMemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await AIMemoryService.update_memory(db=db, user_id=current_user.id, memory_id=memory_id, payload=payload)


@router.delete("/memories/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await AIMemoryService.delete_memory(db=db, user_id=current_user.id, memory_id=memory_id)
