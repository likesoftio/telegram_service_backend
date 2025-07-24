from typing import Optional, List
from pydantic import EmailStr
from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.base_model import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[EmailStr] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String)
    first_name: Mapped[Optional[str]] = mapped_column(String)
    last_name: Mapped[Optional[str]] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    projects: Mapped[List["Project"]] = relationship("Project", back_populates="user")
    telegram_integrations: Mapped[List["TelegramIntegration"]] = relationship("TelegramIntegration",
                                                                              back_populates="user")
    monitored_channels: Mapped[List["MonitoredChannel"]] = relationship("MonitoredChannel",
                                                                        back_populates="user")
    messages: Mapped[List["Message"]] = relationship("Message", foreign_keys="Message.user_id",
                                                     back_populates="user")
    daily_stats: Mapped[List["MessageStatsDaily"]] = relationship("MessageStatsDaily", 
                                                                  back_populates="user")
