from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    subproject_id = Column(Integer, ForeignKey("subprojects.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    settings_versions = relationship("PromptSettingsVersion", back_populates="prompt_template")