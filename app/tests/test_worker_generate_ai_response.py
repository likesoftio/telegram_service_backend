import pytest
from app.workers.tasks import generate_ai_response_task
from app.models.message import Message
from app.models.prompt_template import PromptTemplate
from app.models.prompt_settings_version import PromptSettingsVersion
from app.db.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
import asyncio

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@pytest.mark.asyncio
async def test_generate_ai_response(monkeypatch):
    # Мокаем openai.ChatCompletion.create
    monkeypatch.setattr("openai.ChatCompletion.create", lambda **kwargs: type("Resp", (), {
        "choices": [type("Choice", (), {"message": type("Msg", (), {"content": "AI answer"})()})()],
        "model": "gpt-3.5-turbo",
        "usage": type("Usage", (), {"total_tokens": 42})()
    })
    # Добавляем тестовые объекты
    async with SessionLocal() as session:
        prompt = PromptTemplate(name="TestPrompt", description="", subproject_id=1)
        session.add(prompt)
        await session.commit()
        settings_v = PromptSettingsVersion(prompt_template_id=prompt.id, system_prompt="{{ message_text }}", params={"model": "gpt-3.5-turbo"}, version=1, is_active=True)
        session.add(settings_v)
        await session.commit()
        msg = Message(user_id=1, integration_id=1, subproject_id=1, channel_id="@testchan", channel_title="Test Channel", message_id="1", message_text="Test", message_date=None, ai_response_status="PENDING", prompt_template_id=prompt.id, prompt_settings_version=1)
        session.add(msg)
        await session.commit()
        message_id = msg.id
    # Запускаем задачу
    generate_ai_response_task(message_id)
    # Проверяем, что ответ появился
    async with SessionLocal() as session:
        q = await session.execute(
            session.query(Message).filter(Message.id == message_id)
        )
        msg = q.scalar_one_or_none()
        assert msg.ai_response == "AI answer" 