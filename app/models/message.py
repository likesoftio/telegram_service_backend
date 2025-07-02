from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    integration_id = Column(Integer, ForeignKey("telegram_integrations.id"), nullable=False)
    subproject_id = Column(Integer, ForeignKey("subprojects.id"), nullable=False)
    channel_id = Column(String, nullable=False)
    channel_title = Column(String, nullable=True)
    message_id = Column(String, nullable=False)  # Telegram message id
    message_text = Column(Text, nullable=False)
    message_date = Column(DateTime, nullable=False)
    ai_response = Column(Text, nullable=True)
    ai_response_status = Column(String, default="PENDING")  # PENDING, APPROVED, DECLINED, SENT, ERROR
    ai_response_moderator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ai_response_moderation_time = Column(DateTime, nullable=True)
    ai_response_edit = Column(Text, nullable=True)
    ai_response_sent = Column(Boolean, default=False)
    prompt_template_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=True)
    prompt_settings_version = Column(Integer, nullable=True)
    openai_model = Column(String, nullable=True)
    openai_token_usage = Column(Integer, nullable=True)
    openai_latency = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", foreign_keys=[user_id])
    integration = relationship("TelegramIntegration")
    subproject = relationship("Subproject")
    moderator = relationship("User", foreign_keys=[ai_response_moderator_id])
    prompt_template = relationship("PromptTemplate") 