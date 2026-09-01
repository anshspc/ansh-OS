from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, generate_uuid


class AIMemory(Base, TimestampMixin):
    __tablename__ = "ai_memories"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    category = Column(String(50), default="fact", index=True, nullable=False)  # preference, goal, project, fact, behavioral_pattern
    key = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    source = Column(String(100), default="chat", nullable=False)  # chat, explicit, inferred, onboarding
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="memories")
