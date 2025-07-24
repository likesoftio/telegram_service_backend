import os
import openai
import time
from sqlalchemy.future import select
from sqlalchemy import func, cast, Date, case
from datetime import datetime, timedelta
from loguru import logger
from telethon.sync import TelegramClient
from telethon.tl.types import PeerChannel, InputPeerChannel
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import ChannelPrivateError

from src.accounts.models import User
from src.projects.models import Project
from src.telegram.models import TelegramIntegration, MonitoredChannel
from src.prompt.models import Message, PromptTemplate, PromptSettingsVersion, MessageStatsDaily
from src.prompt.enums import AIResponseStatus
from src.core.celery_app import celery
from src.core.settings import settings
from src.core.database import SyncSessionLocal
from src.core.encryption import encryption_service
from src.ai_task.service import filter_messages_with_ai, generate_ai_response


@celery.task
def scan_channels_task(
    user_id: int = None,
) -> str:
    """Scans channels using Telethon and saves new messages to the database."""
    try:
        # Создаем клиент OpenAI
        openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        with SyncSessionLocal() as session:
            if user_id:
                q = session.execute(select(MonitoredChannel).where(
                    MonitoredChannel.is_active == True,
                    MonitoredChannel.user_id == user_id
                ))
            else:
                q = session.execute(select(MonitoredChannel).where(MonitoredChannel.is_active == True))
            channels = q.scalars().all()

            for ch in channels:
                integration = ch.integration
                session_path = os.path.join("/code/sessions_dir", integration.session_file)
                
                try:
                    decrypted_api_hash = encryption_service.decrypt(integration.telegram_api_hash)
                    client = TelegramClient(session_path, integration.telegram_api_id, decrypted_api_hash)
                    client.start()

                    linked_chat_id = None
                    try:
                        entity = client.get_entity(ch.channel_id)
                        input_peer = client.get_input_entity(entity)
                        full = client(GetFullChannelRequest(channel=input_peer))
                        
                        # Просто получаем linked_chat_id без дополнительных проверок
                        linked_chat_id = getattr(full.full_chat, 'linked_chat_id', None)
                        
                        # Если 0 или None, устанавливаем None
                        if linked_chat_id == 0 or linked_chat_id is None:
                            linked_chat_id = None
                            
                    except Exception as e:
                        logger.error(f"Ошибка получения linked_chat_id для канала {ch.channel_id}: {e}")
                        linked_chat_id = None
                    
                    # Получаем сообщения
                    messages = list(client.iter_messages(ch.channel_id, limit=10))
                    
                    # Сначала проверяем, какие сообщения уже есть в БД
                    existing_message_ids = set()
                    for msg in messages:
                        q2 = session.execute(select(Message).where(
                            Message.channel_id == ch.channel_id,
                            Message.message_id == str(msg.id)
                        ))
                        exists = q2.scalar_one_or_none()
                        if exists:
                            existing_message_ids.add(str(msg.id))
                    
                    # Фильтруем только новые сообщения
                    new_messages = [msg for msg in messages if str(msg.id) not in existing_message_ids]
                    
                    # Если есть новые сообщения, применяем ИИ фильтр
                    if new_messages:
                        if ch.prompt_filter:
                            # Применяем ИИ фильтр только к новым сообщениям
                            suitable_ids = filter_messages_with_ai(
                                ch.prompt_filter, 
                                new_messages, 
                                openai_client
                            )
                            # Преобразуем в set для быстрого поиска
                            suitable_ids_set = set(str(id) for id in suitable_ids)
                        else:
                            # Если фильтра нет, берем все новые сообщения
                            suitable_ids_set = set(str(msg.id) for msg in new_messages)
                        
                        # Добавляем только подходящие новые сообщения
                        for msg in new_messages:
                            if str(msg.id) in suitable_ids_set:
                                new_msg = Message(
                                    user_id=ch.user_id,
                                    integration_id=ch.integration_id,
                                    project_id=ch.project_id,
                                    channel_id=ch.channel_id,
                                    chat_id=linked_chat_id,
                                    channel_title=ch.channel_title,
                                    message_id=str(msg.id),
                                    message_text=msg.text or "",
                                    message_date=msg.date,
                                    ai_response_status=AIResponseStatus.SAVED,
                                    created_at=datetime.utcnow()
                                )
                                session.add(new_msg)
                                session.commit()
                    
                    client.disconnect()
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Ошибка для канала {ch.channel_id}: {e}")

        logger.info("scan_channels_task: success")
        return "scanned"

    except Exception as e:
        logger.error(f"scan_channels_task error: {e}")
        return f"error: {e}"


@celery.task
def generate_ai_response_task(
    message_id: int,
    user_id: int
):
    """Generates AI response using OpenAI and saves it to the database."""
    try:
        with SyncSessionLocal() as session:
            # Получаем сообщение
            q = session.execute(select(Message).where(Message.id == message_id, Message.user_id == user_id))
            msg = q.scalar_one_or_none()
            
            if not msg:
                logger.error(f"Message {message_id} not found")
                return "Message not found"
            
            # Проверяем, есть ли prompt_template_id
            if not msg.prompt_template_id:
                logger.error(f"Message {message_id} has no prompt_template_id")
                return "No prompt template assigned"
            
            # Получаем активный prompt и параметры
            q2 = session.execute(
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
            

            try:
                # Создаем клиент OpenAI
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                
                # Засекаем время
                start = datetime.utcnow()
                
                # Генерируем ИИ ответ
                ai_response, token_usage, model_name = generate_ai_response(
                    user_prompt=prompt_settings.system_prompt,  # Промпт пользователя
                    message_text=msg.message_text,  # Текст сообщения
                    openai_client=client,
                    model_params=prompt_settings.params  # Параметры модели
                )
                
                # Вычисляем латентность
                latency = (datetime.utcnow() - start).total_seconds()
                
                # Сохраняем результат
                msg.ai_response = ai_response
                msg.ai_response_status = AIResponseStatus.ANSWERED
                msg.prompt_settings_version = prompt_settings.version
                msg.openai_model = model_name
                msg.openai_token_usage = token_usage
                msg.openai_latency = latency
                
                session.commit()
                session.refresh(msg)
                
                logger.info(f"AI response generated for message {message_id}")
                return "ai_response_generated"
                
            except Exception as e:
                msg.ai_response_status = AIResponseStatus.ERROR
                session.commit()
                logger.error(f"OpenAI error for message {message_id}: {e}")
                return f"error: {e}"
                
    except Exception as e:
        logger.error(f"generate_ai_response_task error: {e}")
        return f"error: {e}"


@celery.task
def aggregate_user_stats_daily():
    """Aggregates daily user statistics and saves them to the database."""
    try:
        with SyncSessionLocal() as session:
            # Рассчитываем дату за вчера
            target_date = (datetime.utcnow() - timedelta(days=1)).date()

            # Запрос с группировкой и условными суммами
            q = session.execute(
                select(
                    cast(Message.message_date, Date).label("date"),
                    Message.user_id,
                    func.count().label("messages_scanned"),
                    func.sum(
                        case(
                            (Message.ai_response.isnot(None), 1),
                            else_=0
                        )
                    ).label("messages_with_ai_response"),
                    func.sum(
                        case(
                            (Message.ai_response_sent == True, 1),
                            else_=0
                        )
                    ).label("messages_sent"),
                    func.sum(
                        case(
                            (Message.ai_response_status == AIResponseStatus.PENDING, 1),
                            else_=0
                        )
                    ).label("messages_with_errors"),
                    func.avg(Message.openai_latency).label("avg_ai_generation_time"),
                    func.sum(func.coalesce(Message.openai_token_usage, 0)).label("total_tokens_used")
                )
                .where(cast(Message.message_date, Date) == target_date)
                .group_by(cast(Message.message_date, Date), Message.user_id)
            )

            # Сохраняем или обновляем статистику по каждому пользователю
            for row in q:
                existing_stat = session.execute(
                    select(MessageStatsDaily).where(
                        MessageStatsDaily.user_id == row.user_id,
                        MessageStatsDaily.date == row.date
                    )
                ).scalar_one_or_none()

                if existing_stat:
                    # Обновляем поля
                    existing_stat.messages_scanned = row.messages_scanned
                    existing_stat.messages_with_ai_response = row.messages_with_ai_response
                    existing_stat.messages_sent = row.messages_sent
                    existing_stat.messages_with_errors = row.messages_with_errors
                    existing_stat.avg_ai_generation_time = row.avg_ai_generation_time or 0.0
                    existing_stat.total_tokens_used = row.total_tokens_used or 0
                else:
                    # Создаём новую запись
                    stat = MessageStatsDaily(
                        date=row.date,
                        user_id=row.user_id,
                        messages_scanned=row.messages_scanned,
                        messages_with_ai_response=row.messages_with_ai_response,
                        messages_sent=row.messages_sent,
                        messages_with_errors=row.messages_with_errors,
                        avg_ai_generation_time=row.avg_ai_generation_time or 0.0,
                        total_tokens_used=row.total_tokens_used or 0,
                        created_at=datetime.utcnow()
                    )
                    session.add(stat)

            # Завершаем транзакцию
            session.commit()
            logger.info(f"User stats aggregated for {target_date}")

    except Exception as e:
        logger.error(f"aggregate_user_stats_daily error: {e}")
        return f"error: {e}"
    

@celery.task
def aggregate_user_stats_today(user_id: int):
    """Aggregates today's user statistics for a specific user and saves them to the database."""
    try:
        with SyncSessionLocal() as session:
            # Рассчитываем дату за сегодня
            target_date = datetime.utcnow().date()

            # Запрос с группировкой и условными суммами для конкретного пользователя
            q = session.execute(
                select(
                    cast(Message.message_date, Date).label("date"),
                    Message.user_id,
                    func.count().label("messages_scanned"),
                    func.sum(
                        case(
                            (Message.ai_response.isnot(None), 1),
                            else_=0
                        )
                    ).label("messages_with_ai_response"),
                    func.sum(
                        case(
                            (Message.ai_response_sent == True, 1),
                            else_=0
                        )
                    ).label("messages_sent"),
                    func.sum(
                        case(
                            (Message.ai_response_status == AIResponseStatus.PENDING, 1),
                            else_=0
                        )
                    ).label("messages_with_errors"),
                    func.avg(Message.openai_latency).label("avg_ai_generation_time"),
                    func.sum(func.coalesce(Message.openai_token_usage, 0)).label("total_tokens_used")
                )
                .where(
                    cast(Message.message_date, Date) == target_date,
                    Message.user_id == user_id
                )
                .group_by(cast(Message.message_date, Date), Message.user_id)
            )

            # Получаем результат
            row = q.first()
            
            if row:
                # Проверяем, есть ли уже статистика для этого пользователя за сегодня
                existing_stat = session.execute(
                    select(MessageStatsDaily).where(
                        MessageStatsDaily.user_id == user_id,
                        MessageStatsDaily.date == target_date
                    )
                ).scalar_one_or_none()

                if existing_stat:
                    # Обновляем поля
                    existing_stat.messages_scanned = row.messages_scanned
                    existing_stat.messages_with_ai_response = row.messages_with_ai_response
                    existing_stat.messages_sent = row.messages_sent
                    existing_stat.messages_with_errors = row.messages_with_errors
                    existing_stat.avg_ai_generation_time = row.avg_ai_generation_time or 0.0
                    existing_stat.total_tokens_used = row.total_tokens_used or 0
                else:
                    # Создаём новую запись
                    stat = MessageStatsDaily(
                        date=row.date,
                        user_id=row.user_id,
                        messages_scanned=row.messages_scanned,
                        messages_with_ai_response=row.messages_with_ai_response,
                        messages_sent=row.messages_sent,
                        messages_with_errors=row.messages_with_errors,
                        avg_ai_generation_time=row.avg_ai_generation_time or 0.0,
                        total_tokens_used=row.total_tokens_used or 0,
                        created_at=datetime.utcnow()
                    )
                    session.add(stat)

                # Завершаем транзакцию
                session.commit()
                logger.info(f"User stats aggregated for user {user_id} on {target_date}")
                return f"Stats created for user {user_id}"
            else:
                logger.info(f"No messages found for user {user_id} on {target_date}")
                return f"No data for user {user_id}"

    except Exception as e:
        logger.error(f"aggregate_user_stats_today error for user {user_id}: {e}")
        return f"error: {e}"