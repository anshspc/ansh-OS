"""Voice configuration for Personalix Voice assistant."""
from pydantic import BaseModel, Field
from typing import Optional


class VoiceSettings(BaseModel):
    """Per-user voice settings persisted in preferences."""
    # TTS Settings
    voice_name: str = Field(default="", description="Browser voice name (empty = system default)")
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    voice_pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    auto_speak: bool = Field(default=True, description="Automatically speak AI responses in voice mode")
    language: str = Field(default="en-US", description="STT/TTS language code")

    # Behaviour
    proactive_mode: bool = Field(default=False, description="AI proactively surfaces reminders")
    proactive_interval_minutes: int = Field(default=15, ge=5, le=60)

    # Privacy
    save_transcripts: bool = Field(default=True, description="Persist voice conversation text")
    voice_history_enabled: bool = Field(default=True)
    wake_word_enabled: bool = Field(default=False, description="Future: 'Hey Personalix' trigger")

    # Confirmation thresholds
    confirm_destructive_actions: bool = Field(default=True)


class VoiceChatRequest(BaseModel):
    """Incoming voice chat payload from the browser."""
    transcript: str = Field(..., description="STT transcript from browser")
    conversation_id: Optional[str] = None
    screen_context: Optional[dict] = Field(
        default=None,
        description="Current page / entity visible to the user",
    )
    language: str = Field(default="en-US")
    provider: Optional[str] = None
    input_type: str = Field(default="voice")


class VoiceChatResponse(BaseModel):
    """Response from the voice AI pipeline."""
    conversation_id: str
    message_id: str
    reply: str
    provider: str
    model: str
    tool_calls: list = Field(default_factory=list)
    tokens_used: int = 0
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None
    input_type: str = "voice"
