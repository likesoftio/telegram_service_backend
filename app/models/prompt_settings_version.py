from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class PromptSettingsVersion(Base):
    __tablename__ = "prompt_settings_versions"
    id = Column(Integer, primary_key=True, index=True)
    prompt_template_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=False)
    system_prompt = Column(Text, nullable=False)
    params = Column(JSON, nullable=True)
    version = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    prompt_template = relationship("PromptTemplate", back_populates="settings_versions")