from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, generate_uuid


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    goal_id = Column(String(36), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="todo", index=True, nullable=False)  # inbox, todo, in_progress, completed, archived
    priority = Column(String(50), default="medium", index=True, nullable=False)  # critical, high, medium, low
    
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    estimated_duration = Column(Integer, default=30, nullable=False)  # in minutes
    actual_duration = Column(Integer, default=0, nullable=False)  # in minutes
    
    tags = Column(JSON, default=list, nullable=False)
    recurring = Column(Boolean, default=False, nullable=False)
    recurrence_rule = Column(String(100), nullable=True)  # daily, weekly, monthly
    position = Column(Integer, default=0, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")
    subtasks = relationship("Subtask", back_populates="task", cascade="all, delete-orphan", order_by="Subtask.position")


class Subtask(Base, TimestampMixin):
    __tablename__ = "subtasks"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    position = Column(Integer, default=0, nullable=False)

    task = relationship("Task", back_populates="subtasks")


class TaskDependency(Base, TimestampMixin):
    __tablename__ = "task_dependencies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    depends_on_task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
