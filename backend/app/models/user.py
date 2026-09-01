from sqlalchemy import Boolean, Column, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, generate_uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    role = Column(String(50), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    has_onboarded = Column(Boolean, default=False, nullable=False)
    preferences = Column(JSON, default=lambda: {
        "theme": "system",
        "working_hours_start": "09:00",
        "working_hours_end": "18:00",
        "productivity_style": "deep_work",
        "ai_creativity": "balanced",
        "daily_reminder": True
    }, nullable=False)

    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")
    daily_plans = relationship("DailyPlan", back_populates="user", cascade="all, delete-orphan")
    weekly_reviews = relationship("WeeklyReview", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("AIMemory", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("AIConversation", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base, TimestampMixin):
    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), index=True, nullable=False)
    refresh_token = Column(String(512), unique=True, index=True, nullable=False)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    is_revoked = Column(Boolean, default=False, nullable=False)
