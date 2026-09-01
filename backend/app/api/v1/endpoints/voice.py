"""Voice API endpoints for Personalix Voice assistant."""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.voice.voice_config import VoiceChatRequest, VoiceChatResponse, VoiceSettings
from app.voice.voice_router import route_voice_request

router = APIRouter()

# In-memory per-user voice settings store (upgradeable to DB column later)
_voice_settings_store: Dict[str, dict] = {}


@router.post("/chat", response_model=VoiceChatResponse)
async def voice_chat(
    payload: VoiceChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Primary voice endpoint.
    Receives an STT transcript from the browser, routes it through the
    AI pipeline with voice-specific context enrichment, and returns a
    plain-text response ready for TTS.
    """
    result = await route_voice_request(db=db, user=current_user, request=payload)
    return result


@router.get("/settings", response_model=VoiceSettings)
async def get_voice_settings(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Return this user's voice configuration."""
    stored = _voice_settings_store.get(current_user.id, {})
    return VoiceSettings(**stored)


@router.put("/settings", response_model=VoiceSettings)
async def update_voice_settings(
    settings: VoiceSettings,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Persist updated voice settings for this user."""
    _voice_settings_store[current_user.id] = settings.model_dump()
    return settings


@router.get("/history")
async def get_voice_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Return recent voice conversation messages.
    Voice messages are stored in the same AIMessage table with
    input_type='voice' — this endpoint filters for them.
    """
    from sqlalchemy import select, desc
    from app.models.ai_conversation import AIMessage, AIConversation

    stmt = (
        select(AIMessage)
        .join(AIConversation, AIMessage.conversation_id == AIConversation.id)
        .where(
            AIConversation.user_id == current_user.id,
            AIMessage.role.in_(["user", "assistant"]),
        )
        .order_by(desc(AIMessage.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return [
        {
            "id": m.id,
            "conversation_id": m.conversation_id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in reversed(messages)
    ]


@router.get("/capabilities")
async def get_voice_capabilities() -> Dict[str, Any]:
    """
    Returns server-side voice feature flags.
    The browser uses this to decide which STT/TTS providers are available.
    """
    return {
        "stt_providers": ["browser_web_speech"],
        "tts_providers": ["browser_web_speech"],
        "supported_languages": [
            {"code": "en-US", "label": "English (US)"},
            {"code": "en-IN", "label": "English (India / Hinglish)"},
            {"code": "hi-IN", "label": "Hindi"},
            {"code": "en-GB", "label": "English (UK)"},
        ],
        "wake_word_supported": False,
        "proactive_mode_supported": True,
        "version": "1.0.0",
    }
