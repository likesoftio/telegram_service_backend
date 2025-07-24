import time
import os
from fastapi import Depends, HTTPException
from collections.abc import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from telethon import TelegramClient

from src.core.database import get_async_session
from src.core.encryption import encryption_service
from src.projects.models import Project
from src.projects.services.service import get_project
from src.accounts.models import User
from src.telegram.models import TelegramIntegration, MonitoredChannel
from src.telegram.api.v1.schemas import (
    ChannelRequest,
    ChannelUpdateRequest,
    MTProtoRequest,
    MTProtoResponse,
    ConfirmCodeRequest
)


SESSIONS_DIR = "/code/sessions_dir"


async def create_mtproto_integration(
    payload: MTProtoRequest,
    user: User,
) -> MTProtoResponse:
    try:
        temp_session = f"temp_{user.id}_{int(time.time())}"
        temp_session_path = os.path.join(SESSIONS_DIR, temp_session)

        temp_client = TelegramClient(temp_session_path, payload.telegram_api_id, payload.telegram_api_hash)

        await temp_client.connect()

        sent_code = await temp_client.send_code_request(payload.phone_number)

        await temp_client.disconnect()

        response = MTProtoResponse(
            status="success",
            phone_code_hash=sent_code.phone_code_hash,
            temp_session=temp_session
        )
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create MTProto integration: {str(e)}")


async def confirm_mtproto_code(
    payload: ConfirmCodeRequest,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> TelegramIntegration:
    try:
        temp_session_path = os.path.join(SESSIONS_DIR, payload.temp_session)
        temp_client = TelegramClient(temp_session_path, payload.telegram_api_id, payload.telegram_api_hash)
        await temp_client.connect()

        await temp_client.sign_in(payload.phone_number, payload.code, phone_code_hash=payload.phone_code_hash)

        temp_session_path = os.path.join(SESSIONS_DIR, payload.temp_session)
        final_session_path = os.path.join(SESSIONS_DIR, f"user_{user.id}_mtproto")

        if os.path.exists(f"{temp_session_path}.session"):
            os.rename(f"{temp_session_path}.session", f"{final_session_path}.session")

        integration = TelegramIntegration(
            name=payload.name,
            phone_number=payload.phone_number,
            telegram_api_id=payload.telegram_api_id,
            telegram_api_hash=encryption_service.encrypt(payload.telegram_api_hash),
            user_id=user.id,
            session_file=f"user_{user.id}_mtproto",
        )

        session.add(integration)
        await session.commit()
        await session.refresh(integration)

        await temp_client.disconnect()
        return integration

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to confirm MTProto code: {str(e)}")


async def list_alies_integrations(
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[TelegramIntegration]:
    q = await session.execute(select(TelegramIntegration).where(TelegramIntegration.user_id == user.id))
    return q.scalars().all()


async def get_alies_integrations(
    integration_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> TelegramIntegration:
    query = await session.execute(select(TelegramIntegration).where(
        TelegramIntegration.id == integration_id,
                    TelegramIntegration.user_id == user.id
        )
    )

    integration = query.scalar_one_or_none()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    return integration


async def delete_alies_integrations(
    integration_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> None:
    integration = await get_alies_integrations(integration_id, user, session)

    await session.delete(integration)
    await session.commit()

    return None


async def create_channel(
    payload: ChannelRequest,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> MonitoredChannel:
    await get_alies_integrations(payload.integration_id, user, session)
    await get_project(payload.project_id, user, session)

    integration_payload = payload.dict(exclude_unset=True)

    channel = MonitoredChannel(**integration_payload, user_id=user.id)

    session.add(channel)
    await session.commit()
    await session.refresh(channel)

    return channel


async def list_alies_channels(
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[MonitoredChannel]:
    q = await session.execute(select(MonitoredChannel).where(MonitoredChannel.user_id == user.id))

    return q.scalars().all()


async def get_alies_channel(
    channel_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> MonitoredChannel:
    q = await session.execute(select(MonitoredChannel).where(
        MonitoredChannel.id == channel_id,
        MonitoredChannel.user_id == user.id)
    )
    channel = q.scalar_one_or_none()

    if not channel:
         raise HTTPException(status_code=404, detail="Channel not found")

    return channel


async def get_channels_for_integration(
    integration_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[MonitoredChannel]:
    await get_alies_integrations(integration_id, user, session)

    q = await session.execute(select(MonitoredChannel).join(TelegramIntegration).where(
        TelegramIntegration.id == integration_id,
        MonitoredChannel.user_id == user.id)
    )
    return q.scalars().all()


async def get_channels_for_project(
    project_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[MonitoredChannel]:
    await get_project(project_id, user, session)

    q = await session.execute(select(MonitoredChannel).join(Project).where(
        Project.id == project_id,
        MonitoredChannel.user_id == user.id)
    )
    return q.scalars().all()


async def update_channel(
    channel_id: int,
    payload: ChannelUpdateRequest,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> MonitoredChannel:
    channel = await get_alies_channel(channel_id, user, session)

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(channel, field, value)

    await session.commit()
    await session.refresh(channel)

    return channel


async def delete_channel(
    channel_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> None:
    channel = await get_alies_channel(channel_id, user, session)

    await session.delete(channel)
    await session.commit()

    return None