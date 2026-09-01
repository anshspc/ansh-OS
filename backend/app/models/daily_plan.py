from sqlalchemy import Column, ForeignKey, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, generate_uuid


class DailyPlan(Base, TimestampMixin):
    __tablename__ = "daily_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    plan_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    summary = Column(Text, nullable=True)
    time_blocks_json = Column(JSON, default=list, nullable=False)
    focus_areas_json = Column(JSON, default=list, nullable=False)
    status = Column(String(50), default="active", nullable=False)  # generated, accepted, modified, completed

    user = relationship("User", back_populates="daily_plans")
