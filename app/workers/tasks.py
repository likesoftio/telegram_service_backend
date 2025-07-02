from app.core.celery_app import celery
from app.models.monitored_channel import MonitoredChannel
from app.models.message import Message
from app.models.prompt_template import PromptTemplate
from app.models.prompt_settings_version import PromptSettingsVersion
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from datetime import datetime, timedelta
import openai
import asyncio
import random
from loguru import logger
import os
from telethon import TelegramClient
from jinja2 import Template, TemplateError
from app.models.message_stats_daily import MessageStatsDaily
from sqlalchemy import func, cast, Date

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "123456"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "your_api_hash")

@celery.task
def scan_channels_task():
    """Сканирует каналы через Telethon и сохраняет новые сообщения в БД."""
    try:
        async def _scan():
            async with SessionLocal() as session:
                q = await session.execute(select(MonitoredChannel).where(MonitoredChannel.is_active == True))
                channels = q.scalars().all()
                for ch in channels:
                    # Только MTProto интеграции (type=mtproto)
                    integration = ch.integration
                    if not integration or integration.type != "mtproto" or not integration.session_file:
                        logger.info(f"Пропускаю канал {ch.channel_id}: не MTProto или нет session_file")
                        continue
                    session_path = integration.session_file
                    try:
                        client = TelegramClient(session_path, TELEGRAM_API_ID, TELEGRAM_API_HASH)
                        await client.start()
                        # Получаем последние 10 сообщений
                        async for msg in client.iter_messages(ch.channel_id, limit=10):
                            # Проверяем, есть ли уже такое сообщение в БД
                            q2 = await session.execute(select(Message).where(
                                Message.channel_id == ch.channel_id,
                                Message.message_id == str(msg.id)
                            ))
                            exists = q2.scalar_one_or_none()
                            if exists:
                                continue
                            # Сохраняем новое сообщение
                            new_msg = Message(
                                user_id=ch.user_id,
                                integration_id=ch.integration_id,
                                subproject_id=ch.subproject_id,
                                channel_id=ch.channel_id,
                                channel_title=ch.channel_title,
                                message_id=str(msg.id),
                                message_text=msg.text or "",
                                message_date=msg.date,
                                ai_response_status="PENDING",
                                created_at=datetime.utcnow()
                            )
                            session.add(new_msg)
                        await session.commit()
                        await client.disconnect()
                        logger.info(f"Канал {ch.channel_id}: новые сообщения сохранены")
                    except Exception as e:
                        logger.error(f"Ошибка Telethon для {ch.channel_id}: {e}")
        asyncio.run(_scan())
        logger.info("scan_channels_task: success")
        return "scanned"
    except Exception as e:
        logger.error(f"scan_channels_task error: {e}")
        return f"error: {e}"

@celery.task
def generate_ai_response_task(message_id: int):
    """Генерирует AI-ответ через OpenAI и сохраняет в БД."""
    try:
        async def _generate():
            async with SessionLocal() as session:
                q = await session.execute(select(Message).where(Message.id == message_id))
                msg = q.scalar_one_or_none()
                if not msg:
                    logger.error(f"Message {message_id} not found")
                    return "Message not found"
                # Получаем активный prompt и параметры
                q2 = await session.execute(
                    select(PromptTemplate, PromptSettingsVersion)
                    .where(PromptTemplate.id == msg.prompt_template_id)
                    .join(PromptSettingsVersion, PromptSettingsVersion.prompt_template_id == PromptTemplate.id)
                    .where(PromptSettingsVersion.is_active == True)
                )
                res = q2.first()
                if not res:
                    logger.error(f"No active prompt settings for message {message_id}")
                    return "No active prompt settings"
                prompt_template, prompt_settings = res
                # Формируем prompt через Jinja2
                try:
                    template = Template(prompt_settings.system_prompt)
                    prompt = template.render(
                        message_text=msg.message_text,
                        channel_title=msg.channel_title,
                        params=prompt_settings.params or {},
                        user_id=msg.user_id,
                        message_id=msg.message_id
                    )
                except TemplateError as te:
                    msg.ai_response_status = "ERROR"
                    await session.commit()
                    logger.error(f"Jinja2 error for message {message_id}: {te}")
                    return f"jinja2 error: {te}"
                openai.api_key = settings.OPENAI_API_KEY
                try:
                    start = datetime.utcnow()
                    response = openai.ChatCompletion.create(
                        model=prompt_settings.params.get("model", "gpt-3.5-turbo"),
                        messages=[{"role": "system", "content": prompt}],
                        max_tokens=prompt_settings.params.get("max_tokens", 256),
                        temperature=prompt_settings.params.get("temperature", 0.7),
                    )
                    latency = (datetime.utcnow() - start).total_seconds()
                    msg.ai_response = response.choices[0].message.content
                    msg.ai_response_status = "PENDING"
                    msg.openai_model = response.model
                    msg.openai_token_usage = response.usage.total_tokens
                    msg.openai_latency = latency
                    await session.commit()
                    await session.refresh(msg)
                    logger.info(f"AI response generated for message {message_id}")
                    return "ai_response_generated"
                except Exception as e:
                    msg.ai_response_status = "ERROR"
                    await session.commit()
                    logger.error(f"OpenAI error for message {message_id}: {e}")
                    return f"error: {e}"
        asyncio.run(_generate())
        return "done"
    except Exception as e:
        logger.error(f"generate_ai_response_task error: {e}")
        return f"error: {e}"

@celery.task
def aggregate_message_stats_daily():
    """Агрегирует статистику по сообщениям за вчера и сохраняет в message_stats_daily."""
    try:
        async def _aggregate():
            async with SessionLocal() as session:
                # За вчера
                target_date = (datetime.utcnow() - timedelta(days=1)).date()
                # Группировка по prompt_template_id, prompt_settings_version, moderator_id
                q = await session.execute(
                    select(
                        cast(Message.message_date, Date).label("date"),
                        Message.prompt_template_id,
                        Message.prompt_settings_version,
                        Message.ai_response_moderator_id,
                        func.count().label("messages_total"),
                        func.sum(func.case((Message.ai_response_status == "APPROVED", 1), else_=0)).label("approved"),
                        func.sum(func.case((Message.ai_response_status == "DECLINED", 1), else_=0)).label("declined"),
                        func.sum(func.case((Message.ai_response_status == "SENT", 1), else_=0)).label("sent"),
                        func.sum(func.case((Message.liked_by_user == True, 1), else_=0)).label("liked_messages"),
                        func.avg(func.extract('epoch', Message.ai_response_moderation_time - Message.created_at)).label("avg_moderation_time")
                    )
                    .where(cast(Message.message_date, Date) == target_date)
                    .group_by(
                        cast(Message.message_date, Date),
                        Message.prompt_template_id,
                        Message.prompt_settings_version,
                        Message.ai_response_moderator_id
                    )
                )
                for row in q:
                    stat = MessageStatsDaily(
                        date=row.date,
                        prompt_template_id=row.prompt_template_id,
                        prompt_settings_version=row.prompt_settings_version,
                        moderator_id=row.ai_response_moderator_id,
                        messages_total=row.messages_total,
                        approved=row.approved,
                        declined=row.declined,
                        sent=row.sent,
                        liked_messages=row.liked_messages,
                        avg_moderation_time=row.avg_moderation_time or 0.0,
                        created_at=datetime.utcnow()
                    )
                    session.add(stat)
                await session.commit()
                logger.info(f"Stats aggregated for {target_date}")
        asyncio.run(_aggregate())
        return "aggregated"
    except Exception as e:
        logger.error(f"aggregate_message_stats_daily error: {e}")
        return f"error: {e}" 