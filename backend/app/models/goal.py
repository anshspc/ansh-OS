from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, generate_uuid


class Goal(Base, TimestampMixin):
    __tablename__ = "goals"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="career", index=True, nullable=False)  # career, learning, health, finance, personal
    target_date = Column(DateTime(timezone=True), nullable=True)
    progress = Column(Float, default=0.0, nullable=False)
    status = Column(String(50), default="in_progress", index=True, nullable=False)  # in_progress, achieved, paused, cancelled
    color = Column(String(50), default="#10b981", nullable=False)
    icon = Column(String(50), default="target", nullable=False)
    metrics = Column(JSON, default=dict, nullable=False)  # e.g., {"current": 5, "target": 10, "unit": "problems"}

    # Relationships
    user = relationship("User", back_populates="goals")
    projects = relationship("Project", back_populates="goal")
    tasks = relationship("Task", back_populates="goal")
    habits = relationship("Habit", back_populates="goal")
    milestones = relationship("GoalMilestone", back_populates="goal", cascade="all, delete-orphan", order_by="GoalMilestone.position")
    notes = relationship("Note", back_populates="goal")


class GoalMilestone(Base, TimestampMixin):
    __tablename__ = "goal_milestones"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    goal_id = Column(String(36), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    position = Column(Integer, default=0, nullable=False)

    goal = relationship("Goal", back_populates="milestones")
