from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base


class TelegramIntegration(Base):
    __tablename__ = "telegram_integrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column="users.id", ondelete="CASCADE"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    telegram_api_id: Mapped[int] = mapped_column(Integer, nullable=False)
    telegram_api_hash: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    session_file: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="telegram_integrations")
    monitored_channels: Mapped[List["MonitoredChannel"]] = relationship("MonitoredChannel",
                                                                        back_populates="integration",
                                                                        cascade="all, delete-orphan")
    messages: Mapped[List["Message"]] = relationship("Message",
                                                     back_populates="integration",
                                                     cascade="all, delete-orphan")


class MonitoredChannel(Base):
    __tablename__ = "monitored_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    integration_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column="telegram_integrations.id", ondelete="CASCADE"),
        nullable=False
    )
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column="projects.id", ondelete="CASCADE"),
        nullable=False
    )
    channel_id: Mapped[str] = mapped_column(String, nullable=False)
    channel_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    prompt_filter: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="monitored_channels")
    integration: Mapped["TelegramIntegration"] = relationship("TelegramIntegration",
                                                              back_populates="monitored_channels")
    project: Mapped["Project"] = relationship("Project", back_populates="monitored_channels")