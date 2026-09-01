from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, generate_uuid


class ActivityLog(Base, TimestampMixin):
    __tablename__ = "activity_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)  # task_created, task_completed, habit_logged, note_created, etc.
    entity_type = Column(String(50), nullable=False, index=True)  # task, project, habit, goal, note, document
    entity_id = Column(String(36), nullable=True)
    details = Column(JSON, default=dict, nullable=False)

    user = relationship("User", back_populates="activity_logs")
