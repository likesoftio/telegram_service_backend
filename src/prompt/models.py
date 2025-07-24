from typing import Optional, Dict, Any, List
from datetime import datetime, date
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Date, BigInteger
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base
from src.prompt.enums import AIResponseStatus


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column="projects.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    settings_versions: Mapped[List["PromptSettingsVersion"]] = relationship("PromptSettingsVersion",
                                                                            back_populates="prompt_template",
                                                                            cascade="all, delete-orphan")
    project: Mapped["Project"] = relationship("Project", back_populates="prompt_templates")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="prompt_template")


class PromptSettingsVersion(Base):
    __tablename__ = "prompt_settings_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prompt_template_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column="prompt_templates.id", ondelete="CASCADE"),
        nullable=False
    )
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    params: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    prompt_template: Mapped["PromptTemplate"] = relationship("PromptTemplate", back_populates="settings_versions")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column="users.id", ondelete="CASCADE"),
        nullable=False
    )
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
    chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    channel_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    message_id: Mapped[str] = mapped_column(String, nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    message_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    ai_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_response_status: Mapped[AIResponseStatus] = mapped_column(
        SQLEnum(AIResponseStatus, name="ai_response_status_enum"),
        default=AIResponseStatus.PENDING,
        nullable=False
    )
    ai_response_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    prompt_template_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(column="prompt_templates.id", ondelete="CASCADE"),
        nullable=True
    )
    prompt_settings_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    openai_model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    openai_token_usage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    openai_latency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="messages")
    integration: Mapped["TelegramIntegration"] = relationship(
                                                "TelegramIntegration",
                                                lazy="selectin",
                                                back_populates="messages")
    project: Mapped["Project"] = relationship("Project", back_populates="messages")
    prompt_template: Mapped["PromptTemplate"] = relationship("PromptTemplate", back_populates="messages")


class MessageStatsDaily(Base):
    __tablename__ = "message_stats_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column="users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Статистика по сообщениям
    messages_scanned: Mapped[int] = mapped_column(Integer, default=0)  # Сколько сообщений собрано с каналов
    messages_with_ai_response: Mapped[int] = mapped_column(Integer, default=0)  # Сколько ИИ ответов сформировано
    messages_sent: Mapped[int] = mapped_column(Integer, default=0)  # Сколько сообщений отправлено
    messages_with_errors: Mapped[int] = mapped_column(Integer, default=0)  # Сколько ошибочных сообщений
    
    # Временные метрики
    avg_ai_generation_time: Mapped[float] = mapped_column(Float, default=0.0)  # Среднее время генерации ИИ
    
    # Дополнительные метрики
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)  # Общее количество токенов
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="daily_stats")