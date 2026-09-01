from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, generate_uuid


class CalendarEvent(Base, TimestampMixin):
    __tablename__ = "calendar_events"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    is_all_day = Column(Boolean, default=False, nullable=False)
    
    event_type = Column(String(50), default="focus", nullable=False)  # focus, meeting, deadline, reminder, personal
    color = Column(String(50), default="#6366f1", nullable=False)
    location = Column(String(255), nullable=True)
    recurrence = Column(String(100), nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)

    user = relationship("User", back_populates="calendar_events")
