from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.ai_memory import AIMemory
from app.schemas.ai import AIMemoryCreate, AIMemoryUpdate


class AIMemoryService:
    @staticmethod
    async def get_memories(
        db: AsyncSession,
        user_id: str,
        category: Optional[str] = None,
        is_active: bool = True,
    ) -> List[AIMemory]:
        stmt = (
            select(AIMemory)
            .where(AIMemory.user_id == user_id, AIMemory.is_active == is_active)
        )
        if category:
            stmt = stmt.where(AIMemory.category == category)
        stmt = stmt.order_by(AIMemory.confidence.desc(), AIMemory.updated_at.desc())

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_memory(
        db: AsyncSession,
        user_id: str,
        payload: AIMemoryCreate,
    ) -> AIMemory:
        memory = AIMemory(
            user_id=user_id,
            category=payload.category,
            key=payload.key,
            content=payload.content,
            confidence=payload.confidence,
            source=payload.source,
        )
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        return memory

    @staticmethod
    async def update_memory(
        db: AsyncSession,
        user_id: str,
        memory_id: str,
        payload: AIMemoryUpdate,
    ) -> AIMemory:
        stmt = select(AIMemory).where(AIMemory.id == memory_id, AIMemory.user_id == user_id)
        result = await db.execute(stmt)
        mem = result.scalar_one_or_none()
        if not mem:
            raise NotFoundException(resource="AI Memory", identifier=memory_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(mem, field, value)

        await db.commit()
        await db.refresh(mem)
        return mem

    @staticmethod
    async def delete_memory(db: AsyncSession, user_id: str, memory_id: str) -> None:
        stmt = select(AIMemory).where(AIMemory.id == memory_id, AIMemory.user_id == user_id)
        result = await db.execute(stmt)
        mem = result.scalar_one_or_none()
        if not mem:
            raise NotFoundException(resource="AI Memory", identifier=memory_id)
        await db.delete(mem)
        await db.commit()

    @staticmethod
    async def extract_and_save_memories_from_text(
        db: AsyncSession,
        user_id: str,
        user_text: str,
    ) -> List[AIMemory]:
        """Heuristically extract preference/fact patterns from chat messages (e.g. 'I prefer morning', 'Remember that I am studying for AWS')."""
        saved = []
        text_lower = user_text.lower()

        # Check for explicit preference keywords
        if "i prefer " in text_lower or "i usually work " in text_lower or "i like to work " in text_lower:
            pref = AIMemory(
                user_id=user_id,
                category="preference",
                content=user_text.strip(),
                confidence=0.9,
                source="chat_inferred",
            )
            db.add(pref)
            saved.append(pref)

        elif "remember that " in text_lower:
            clean_fact = user_text.split("remember that ", 1)[-1].strip()
            fact = AIMemory(
                user_id=user_id,
                category="fact",
                content=clean_fact,
                confidence=0.95,
                source="chat_explicit",
            )
            db.add(fact)
            saved.append(fact)

        if saved:
            await db.commit()
            for s in saved:
                await db.refresh(s)

        return saved
