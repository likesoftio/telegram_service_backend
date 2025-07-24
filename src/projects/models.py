from typing import List
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column="users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="projects")
    monitored_channels: Mapped[List["MonitoredChannel"]] = relationship("MonitoredChannel",
                                                                        back_populates="project")
    prompt_templates: Mapped[List["PromptTemplate"]] = relationship("PromptTemplate",
                                                                    back_populates="project")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="project")