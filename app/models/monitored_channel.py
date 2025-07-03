from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models import *

class MonitoredChannel(Base):
    __tablename__ = "monitored_channels"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    integration_id = Column(Integer, ForeignKey("telegram_integrations.id"), nullable=False)
    subproject_id = Column(Integer, ForeignKey("subprojects.id"), nullable=False)
    channel_id = Column(String, nullable=False)  # Telegram ID или username
    channel_title = Column(String, nullable=True)
    filters = Column(JSON, nullable=True)  # ключевые слова, regexp
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    integration = relationship("TelegramIntegration")
    subproject = relationship("Subproject") 