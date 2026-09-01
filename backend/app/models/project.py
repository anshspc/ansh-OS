from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, generate_uuid


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_id = Column(String(36), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", index=True, nullable=False)  # active, completed, on_hold, archived
    color = Column(String(50), default="#3b82f6", nullable=False)
    icon = Column(String(50), default="folder", nullable=False)
    
    start_date = Column(DateTime(timezone=True), nullable=True)
    target_date = Column(DateTime(timezone=True), nullable=True)
    progress = Column(Float, default=0.0, nullable=False)
    tags = Column(JSON, default=list, nullable=False)

    # Relationships
    user = relationship("User", back_populates="projects")
    goal = relationship("Goal", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan", order_by="Milestone.position")
    notes = relationship("Note", back_populates="project")


class Milestone(Base, TimestampMixin):
    __tablename__ = "milestones"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    position = Column(Integer, default=0, nullable=False)

    project = relationship("Project", back_populates="milestones")
