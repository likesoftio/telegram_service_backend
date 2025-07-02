from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class TelegramIntegration(Base):
    __tablename__ = "telegram_integrations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # 'bot' или 'mtproto'
    name = Column(String, nullable=False)
    bot_token = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    session_file = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")