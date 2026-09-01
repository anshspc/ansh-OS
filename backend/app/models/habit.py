from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, generate_uuid


class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_id = Column(String(36), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(String(50), default="daily", nullable=False)  # daily, weekly
    target_days = Column(JSON, default=lambda: [0, 1, 2, 3, 4, 5, 6], nullable=False)
    reminder_time = Column(String(10), nullable=True)  # "08:00"
    
    streak_count = Column(Integer, default=0, nullable=False)
    best_streak = Column(Integer, default=0, nullable=False)
    color = Column(String(50), default="#8b5cf6", nullable=False)
    icon = Column(String(50), default="activity", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="habits")
    goal = relationship("Goal", back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan", order_by="HabitLog.logged_date.desc()")


class HabitLog(Base, TimestampMixin):
    __tablename__ = "habit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    habit_id = Column(String(36), ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    logged_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    completed = Column(Boolean, default=True, nullable=False)
    value = Column(Float, default=1.0, nullable=False)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint('habit_id', 'logged_date', name='uq_habit_log_date'),
    )

    habit = relationship("Habit", back_populates="logs")
