import json
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.llm_provider import get_llm_provider
from app.ai.tools import AVAILABLE_AI_TOOLS, ToolDispatcher
from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.models.ai_conversation import AIConversation, AIMessage
from app.models.calendar_event import CalendarEvent
from app.models.task import Task
from app.models.user import User
from app.schemas.ai import AIChatRequest, AIChatMessageRequest, AIChatResponse, ToolCallItem
from app.services.ai_memory_service import AIMemoryService
from app.services.vector_service import VectorService


class AIOrchestrator:
    @staticmethod
    async def build_system_context(db: AsyncSession, user: User, user_query: str) -> str:
        """Assemble dynamic multi-layered system context for the AI."""
        # 1. User preferences
        prefs = user.preferences or {}
        working_hours = f"{prefs.get('working_hours_start', '09:00')} to {prefs.get('working_hours_end', '18:00')}"
        style = prefs.get('productivity_style', 'deep_work')

        # 2. Long-term memories
        memories = await AIMemoryService.get_memories(db, user.id, is_active=True)
        memory_str = "\n".join([f"- [{m.category.upper()}] {m.content}" for m in memories[:10]]) if memories else "None yet."

        # 3. High priority active tasks
        stmt_tasks = select(Task).where(
            Task.user_id == user.id,
            Task.status.in_(["todo", "in_progress"]),
        ).order_by(Task.priority.desc()).limit(5)
        res_tasks = await db.execute(stmt_tasks)
        top_tasks = list(res_tasks.scalars().all())
        tasks_str = "\n".join([f"- {t.title} [Priority: {t.priority}, Status: {t.status}]" for t in top_tasks]) if top_tasks else "No active tasks."

        # 4. Relevant knowledge snippets via Vector Search
        search_results = await VectorService.search_knowledge(db, user.id, user_query, limit=3)
        rag_str = "\n".join([f"- [{r.type.upper()}: {r.title}] {r.snippet}" for r in search_results]) if search_results else "None."

        context = f"""You are Personalix OS Assistant, an intelligent, proactive, and concise personal AI operating system.
Your mission is to help {user.full_name} manage their life, tasks, projects, goals, habits, and knowledge.

USER PROFILE:
- Name: {user.full_name}
- Working Hours: {working_hours}
- Productivity Style: {style}

ACTIVE MEMORIES & FACTS:
{memory_str}

CURRENT HIGH-PRIORITY TASKS:
{tasks_str}

RELEVANT KNOWLEDGE CONTEXT (RAG):
{rag_str}

GUIDELINES:
1. Always be action-oriented, helpful, and clear.
2. Use tools to execute actions (create tasks, schedule daily plans, search knowledge, prepare reviews).
3. If an action permanently deletes critical data, ask for confirmation before executing.
4. Format output using clean GitHub-flavored markdown with bullet points and bold headers where appropriate.
"""
        return context

    @staticmethod
    async def process_chat(
        db: AsyncSession,
        user: User,
        payload: AIChatMessageRequest,
    ) -> AIChatResponse:
        """Full agent loop: conversation tracking, context assembly, tool calling, and response generation."""
        # 1. Get or create conversation
        if payload.conversation_id:
            stmt = select(AIConversation).options(selectinload(AIConversation.messages)).where(
                AIConversation.id == payload.conversation_id,
                AIConversation.user_id == user.id,
            )
            result = await db.execute(stmt)
            conversation = result.scalar_one_or_none()
            if not conversation:
                raise NotFoundException(resource="Conversation", identifier=payload.conversation_id)
        else:
            conversation = AIConversation(
                user_id=user.id,
                title=payload.message[:40] + ("..." if len(payload.message) > 40 else ""),
            )
            db.add(conversation)
            await db.flush()

        # 2. Save incoming user message
        user_msg = AIMessage(
            conversation_id=conversation.id,
            role="user",
            content=payload.message,
        )
        db.add(user_msg)
        await db.flush()

        # Extract any potential new memories
        await AIMemoryService.extract_and_save_memories_from_text(db, user.id, payload.message)

        # 3. Assemble LLM message history
        system_prompt = await AIOrchestrator.build_system_context(db, user, payload.message)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add past conversation history (last 8 messages)
        past_msgs = []
        if payload.conversation_id:
            stmt_hist = (
                select(AIMessage)
                .where(AIMessage.conversation_id == conversation.id, AIMessage.id != user_msg.id)
                .order_by(AIMessage.created_at.desc())
                .limit(8)
            )
            res_hist = await db.execute(stmt_hist)
            past_msgs = list(reversed(list(res_hist.scalars().all())))

        for m in past_msgs:
            if m.role in ("user", "assistant"):
                messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": payload.message})

        # 4. Invoke LLM Provider
        provider = get_llm_provider(payload.provider or settings.DEFAULT_AI_PROVIDER)
        llm_response = await provider.chat(
            messages=messages,
            tools=AVAILABLE_AI_TOOLS,
            temperature=payload.temperature or 0.7,
        )

        executed_tool_items: List[ToolCallItem] = []
        final_reply = llm_response["reply"]

        # 5. Handle Tool Calls if returned
        if llm_response.get("tool_calls"):
            for tc in llm_response["tool_calls"]:
                tool_name = tc["name"]
                args = tc["arguments"]
                call_id = tc.get("id", str(uuid.uuid4())[:8])

                tool_result = await ToolDispatcher.dispatch(db, user.id, tool_name, args)
                executed_tool_items.append(
                    ToolCallItem(
                        id=call_id,
                        name=tool_name,
                        arguments=args,
                        result=tool_result,
                        status=tool_result.get("status", "success"),
                    )
                )

            # If tool executed and reply is empty, generate structured tool summary
            if not final_reply.strip():
                summaries = [f"- Executed **{t.name}**: {t.result.get('message', 'Completed')}" for t in executed_tool_items]
                final_reply = "### Actions Performed:\n" + "\n".join(summaries)

        # 6. Save Assistant response message in DB
        assistant_msg = AIMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=final_reply,
            tool_calls=[t.model_dump() for t in executed_tool_items] if executed_tool_items else None,
            tool_results=[t.result for t in executed_tool_items] if executed_tool_items else None,
            model=llm_response.get("model"),
            tokens_used=llm_response.get("tokens_used", 0),
        )
        db.add(assistant_msg)
        await db.commit()
        await db.refresh(assistant_msg)

        return AIChatResponse(
            conversation_id=conversation.id,
            message_id=assistant_msg.id,
            reply=final_reply,
            role="assistant",
            provider=llm_response.get("provider", "offline_heuristic"),
            model=llm_response.get("model", "default"),
            tool_calls=executed_tool_items if executed_tool_items else None,
            tokens_used=llm_response.get("tokens_used", 0),
        )
