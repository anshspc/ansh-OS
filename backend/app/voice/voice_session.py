"""Voice session management for Personalix Voice."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class VoiceSession:
    """
    Tracks a single voice conversation session.
    
    A session starts when the user activates voice mode and persists
    across multiple utterances until the user closes the overlay.
    The conversation_id links to the normal AIConversation so voice
    messages appear in the shared text history.
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    conversation_id: Optional[str] = None

    # Accumulated transcript for context
    transcript_history: list = field(default_factory=list)

    # Current screen context injected per request
    screen_context: dict = field(default_factory=dict)

    # Session metadata
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    utterance_count: int = 0
    language: str = "en-US"

    def add_utterance(self, role: str, text: str, input_type: str = "voice"):
        self.transcript_history.append({
            "role": role,
            "text": text,
            "input_type": input_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if role == "user":
            self.utterance_count += 1

    def update_screen_context(self, context: dict):
        self.screen_context = context or {}

    def to_summary(self) -> str:
        """Return a compact text summary of recent exchanges for context injection."""
        recent = self.transcript_history[-6:]  # last 3 exchanges
        lines = []
        for item in recent:
            prefix = "User said" if item["role"] == "user" else "Personalix replied"
            lines.append(f"[Voice] {prefix}: {item['text']}")
        return "\n".join(lines)
