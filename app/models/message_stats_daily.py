from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class MessageStatsDaily(Base):
    __tablename__ = "message_stats_daily"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    prompt_template_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=False)
    prompt_settings_version = Column(Integer, nullable=False)
    moderator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    messages_total = Column(Integer, default=0)
    approved = Column(Integer, default=0)
    declined = Column(Integer, default=0)
    sent = Column(Integer, default=0)
    liked_messages = Column(Integer, default=0)
    avg_moderation_time = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    prompt_template = relationship("PromptTemplate")
    moderator = relationship("User") 