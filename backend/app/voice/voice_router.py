"""
Voice Router — bridges STT transcript → AI Orchestrator → structured response.

This module adds voice-specific context enrichment on top of the existing
AI Orchestrator so voice and text share the same tool-calling pipeline.
"""
import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.orchestrator import AIOrchestrator
from app.models.user import User
from app.schemas.ai import AIChatRequest
from app.voice.voice_config import VoiceChatRequest, VoiceChatResponse


# Phrases that indicate a potentially destructive / high-risk intent
_DESTRUCTIVE_PATTERNS = [
    r"\bdelete all\b",
    r"\bremove all\b",
    r"\bwipe\b",
    r"\bclear all\b",
    r"\bdrop all\b",
    r"\bpurge\b",
]

_DESTRUCTIVE_RE = re.compile("|".join(_DESTRUCTIVE_PATTERNS), re.IGNORECASE)


def _requires_confirmation(transcript: str) -> tuple[bool, Optional[str]]:
    """Return (True, prompt) if this utterance looks destructive."""
    if _DESTRUCTIVE_RE.search(transcript):
        return True, (
            "This action will permanently modify or delete data. "
            "Please confirm with 'yes' to proceed, or say 'cancel'."
        )
    return False, None


def _build_voice_system_addendum(request: VoiceChatRequest) -> str:
    """
    Build extra context paragraph injected into the system prompt
    for voice sessions.
    """
    parts = [
        "## Voice Mode Active",
        "The user is speaking to you via voice. Keep responses concise and natural — "
        "they will be read aloud by text-to-speech. Avoid markdown, bullet lists, "
        "or code blocks in your reply. Use plain conversational English (or Hindi/Hinglish "
        "if the user speaks that way).",
    ]

    ctx = request.screen_context or {}
    if ctx:
        page = ctx.get("page", "")
        entity = ctx.get("entity_title", "")
        entity_type = ctx.get("entity_type", "")
        if page:
            parts.append(f"The user is currently viewing the **{page}** page.")
        if entity and entity_type:
            parts.append(
                f"They have **{entity_type} '{entity}'** open. "
                "If the user asks 'what's left?' or 'give me an update', "
                "they likely mean this specific item."
            )

    lang = request.language or "en-US"
    if lang.startswith("hi") or lang == "en-IN":
        parts.append(
            "The user may mix Hindi and English (Hinglish). "
            "Understand both and reply in the same language they used."
        )

    return "\n\n" + "\n".join(parts)


async def route_voice_request(
    db: AsyncSession,
    user: User,
    request: VoiceChatRequest,
) -> VoiceChatResponse:
    """
    Main voice routing function.

    1. Check for destructive intent → return confirmation prompt if needed.
    2. Enrich the transcript with screen/voice context addendum.
    3. Delegate to AIOrchestrator (identical to text chat).
    4. Return structured VoiceChatResponse.
    """
    transcript = request.transcript.strip()
    if not transcript:
        return VoiceChatResponse(
            conversation_id=request.conversation_id or "",
            message_id="",
            reply="I didn't catch that. Could you please repeat?",
            provider="fallback",
            model="heuristic",
            input_type="voice",
        )

    # Destructive confirmation gate
    needs_confirm, confirm_prompt = _requires_confirmation(transcript)
    if needs_confirm:
        return VoiceChatResponse(
            conversation_id=request.conversation_id or "",
            message_id="",
            reply=confirm_prompt or "This action requires confirmation. Say 'yes' to proceed.",
            provider="fallback",
            model="heuristic",
            requires_confirmation=True,
            confirmation_prompt=confirm_prompt,
            input_type="voice",
        )

    # Build enriched message with voice context addendum
    voice_addendum = _build_voice_system_addendum(request)
    enriched_transcript = transcript + "\n\n[VOICE_CONTEXT_ADDENDUM]" + voice_addendum

    # Reuse the same text chat pipeline
    chat_request = AIChatRequest(
        message=enriched_transcript,
        conversation_id=request.conversation_id,
        provider=request.provider,
        input_type="voice",
    )

    result = await AIOrchestrator.process_chat(
        db=db,
        user=user,
        payload=chat_request,
    )

    # Strip any markdown formatting from voice responses
    clean_reply = _strip_markdown_for_tts(result.reply)

    return VoiceChatResponse(
        conversation_id=result.conversation_id,
        message_id=result.message_id,
        reply=clean_reply,
        provider=result.provider,
        model=result.model,
        tool_calls=[tc.model_dump() for tc in (result.tool_calls or [])],
        tokens_used=result.tokens_used,
        input_type="voice",
    )


def _strip_markdown_for_tts(text: str) -> str:
    """Remove markdown syntax that would sound bad when spoken."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove inline code
    text = re.sub(r"`[^`]+`", lambda m: m.group(0).strip("`"), text)
    # Remove bold/italic
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    # Remove markdown headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bullet points — replace with natural pauses
    text = re.sub(r"^\s*[-*•]\s+", "  ", text, flags=re.MULTILINE)
    # Remove URLs
    text = re.sub(r"https?://\S+", "a link", text)
    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
