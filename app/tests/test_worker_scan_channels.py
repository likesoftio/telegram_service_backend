import pytest
from app.workers.tasks import scan_channels_task
from app.models.monitored_channel import MonitoredChannel
from app.models.message import Message
from app.db.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
import asyncio

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@pytest.mark.asyncio
async def test_scan_channels_creates_messages(monkeypatch):
    # Мокаем Telethon-клиент, чтобы не обращаться к Telegram
    monkeypatch.setattr("app.workers.tasks.TelegramClient", lambda *a, **kw: type("FakeClient", (), {
        "start": lambda self: None,
        "disconnect": lambda self: None,
        "iter_messages": lambda self, channel_id, limit=10: iter([type("Msg", (), {"id": 1, "text": "Test msg", "date": None})()])
    })
    # Добавляем тестовый канал
    async with SessionLocal() as session:
        ch = MonitoredChannel(
            user_id=1, integration_id=1, subproject_id=1,
            channel_id="@testchan", channel_title="Test Channel", is_active=True
        )
        session.add(ch)
        await session.commit()
    # Запускаем задачу
    scan_channels_task()
    # Проверяем, что сообщение появилось
    async with SessionLocal() as session:
        q = await session.execute(
            session.query(Message).filter(Message.channel_id == "@testchan")
        )
        msgs = q.scalars().all()
        assert any(m.message_text == "Test msg" for m in msgs) 