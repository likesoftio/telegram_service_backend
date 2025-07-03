from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from pydantic import BaseModel

class Subproject(Base):
    __tablename__ = "subprojects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    project = relationship("Project", back_populates="subprojects")

class SubprojectOut(BaseModel):
    id: int
    name: str
    project_id: int
    created_at: str  # или datetime, если фронт поддерживает

    class Config:
        from_attributes = True 