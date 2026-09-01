from sqlalchemy import Column, Float, ForeignKey, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.base import TimestampMixin, generate_uuid


class WeeklyReview(Base, TimestampMixin):
    __tablename__ = "weekly_reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    start_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    end_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    summary = Column(Text, nullable=False)
    wins_json = Column(JSON, default=list, nullable=False)
    bottlenecks_json = Column(JSON, default=list, nullable=False)
    recommendations_json = Column(JSON, default=list, nullable=False)
    productivity_score = Column(Float, default=0.0, nullable=False)
    stats_json = Column(JSON, default=dict, nullable=False)

    user = relationship("User", back_populates="weekly_reviews")
