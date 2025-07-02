import pytest
from app.workers.tasks import aggregate_message_stats_daily
from app.models.message_stats_daily import MessageStatsDaily
from app.models.message import Message
from app.db.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from datetime import datetime, timedelta
import asyncio

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@pytest.mark.asyncio
async def test_aggregate_message_stats_daily():
    # Добавляем тестовое сообщение за вчера
    target_date = (datetime.utcnow() - timedelta(days=1)).date()
    async with SessionLocal() as session:
        msg = Message(user_id=1, integration_id=1, subproject_id=1, channel_id="@testchan", channel_title="Test Channel", message_id="1", message_text="Test", message_date=target_date, ai_response_status="APPROVED", prompt_template_id=1, prompt_settings_version=1, ai_response_moderator_id=1, created_at=target_date)
        session.add(msg)
        await session.commit()
    # Запускаем задачу
    aggregate_message_stats_daily()
    # Проверяем, что статистика появилась
    async with SessionLocal() as session:
        q = await session.execute(
            session.query(MessageStatsDaily).filter(MessageStatsDaily.date == target_date)
        )
        stats = q.scalars().all()
        assert any(s.messages_total > 0 for s in stats) 