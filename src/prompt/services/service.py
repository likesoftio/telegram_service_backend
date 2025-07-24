import os
from fastapi import Depends, HTTPException
from collections.abc import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetDiscussionMessageRequest

from src.core.database import get_async_session
from src.core.encryption import encryption_service
from src.projects.services.service import get_project
from src.projects.models import Project
from src.accounts.models import User
from src.prompt.enums import AIResponseStatus
from src.prompt.services.dataclass import PromptParams
from src.prompt.models import PromptTemplate, PromptSettingsVersion, Message, MessageStatsDaily
from src.prompt.api.v1.schemas import (
    PromptTemplateRequest,
    PromptTemplateUpdate,
    PromptSettingsVersionRequest,
    MessageEdit, MessageAddTemp,
)


async def create_prompt(
    payload: PromptTemplateRequest,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> PromptTemplate:
    await get_project(payload.project_id, user, session)

    update_data = payload.dict(exclude_unset=True)
    prompt = PromptTemplate(**update_data)

    session.add(prompt)
    await session.commit()
    await session.refresh(prompt)

    return prompt


async def list_prompts(
    user: User,
    project_id: int = None,
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[PromptTemplate]:
    q = await session.execute(
        select(PromptTemplate).join(Project).where(Project.user_id == user.id)
    )

    prompts = q.scalars().all()

    if project_id:
        prompts = [p for p in prompts if p.project_id == project_id]

    return prompts


async def get_prompt(
    prompt_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> PromptTemplate:
    query = await session.execute(
        select(PromptTemplate).join(Project).where(
            PromptTemplate.id == prompt_id,
            Project.user_id == user.id
        )
    )
    prompt = query.scalar_one_or_none()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return prompt


async def update_prompt(
    prompt_id: int,
    payload: PromptTemplateUpdate,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> PromptTemplate:
    if payload.project_id:
        await get_project(payload.project_id, user, session)

    prompt = await get_prompt(prompt_id, user, session)

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prompt, key, value)

    await session.commit()
    await session.refresh(prompt)
    return prompt


async def delete_prompt(
    prompt_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> None:
    prompt = await get_prompt(prompt_id, user, session)

    await session.delete(prompt)
    await session.commit()
    return None


async def list_prompt_settings(
    prompt_template_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[PromptSettingsVersion]:
    await get_prompt(prompt_template_id, user, session)

    q2 = await session.execute(
        select(PromptSettingsVersion).where(PromptSettingsVersion.prompt_template_id == prompt_template_id)
    )

    return q2.scalars().all()


async def get_prompt_settings_version(
    prompt_id: int,
    version: int,
    user: User,
    session: AsyncSession
) -> PromptSettingsVersion:
    await get_prompt(prompt_id, user, session)

    settings_query = await session.execute(
        select(PromptSettingsVersion)
        .where(
            PromptSettingsVersion.prompt_template_id == prompt_id,
            PromptSettingsVersion.version == version
        )
    )
    settings = settings_query.scalar_one_or_none()

    if not settings:
        raise HTTPException(
            status_code=404,
            detail=f"Settings version {version} not found for prompt template {prompt_id}"
        )

    return settings


async def create_prompt_settings(
    payload: PromptSettingsVersionRequest,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> PromptSettingsVersion:
    await get_prompt(payload.prompt_template_id, user, session)

    q2 = await session.execute(
        select(func.max(PromptSettingsVersion.version)).where(
            PromptSettingsVersion.prompt_template_id == payload.prompt_template_id
        )
    )
    max_version = q2.scalar() or 0
    version = max_version + 1

    try:
        params = PromptParams.from_dict(payload.params or {})
        payload.params = params.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error validate params: {str(e)}")

    settings_version = PromptSettingsVersion(
        prompt_template_id=payload.prompt_template_id,
        system_prompt=payload.system_prompt,
        params=payload.params,
        version=version,
    )

    session.add(settings_version)
    await session.commit()
    await session.refresh(settings_version)

    return settings_version


async def activate_prompt_settings(
    prompt_id: int,
    version: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> PromptSettingsVersion:
    await get_prompt(prompt_id, user, session)

    await session.execute(
        PromptSettingsVersion.__table__.update().where(PromptSettingsVersion.prompt_template_id == prompt_id).values(is_active=False)
    )

    q2 = await session.execute(
        select(PromptSettingsVersion).where(PromptSettingsVersion.prompt_template_id == prompt_id, PromptSettingsVersion.version == version)
    )
    settings_version = q2.scalar_one_or_none()

    if not settings_version:
        raise HTTPException(status_code=404, detail="Settings version not found")

    settings_version.is_active = True

    await session.commit()
    await session.refresh(settings_version)

    return settings_version


async def get_active_prompt_settings(
    prompt_id: int,
    user: User,
    session: AsyncSession
) -> PromptSettingsVersion:
    await get_prompt(prompt_id, user, session)

    settings_query = await session.execute(
        select(PromptSettingsVersion)
        .where(
            PromptSettingsVersion.prompt_template_id == prompt_id,
            PromptSettingsVersion.is_active == True
        )
    )
    settings = settings_query.scalar_one_or_none()

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="No active settings found for this prompt template"
        )

    return settings


async def list_messages(
    user: User,
    status: AIResponseStatus = AIResponseStatus.PENDING,
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[Message]:
    q = await session.execute(
        select(Message).join(Project)
        .where(Message.ai_response_status == status, Project.user_id == user.id)
    )
    return q.scalars().all()


async def add_prompt_template_for_message(
    payload: MessageAddTemp,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Message:
    await get_prompt(payload.prompt_template_id, user, session)

    message = await get_message(payload.message_id, user, session)

    message.prompt_template_id = payload.prompt_template_id
    await session.commit()
    await session.refresh(message)

    return message


async def get_message(
    message_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Message:
    query = await session.execute(
        select(Message).join(Project)
        .where(Message.id == message_id, Project.user_id == user.id)
    )
    message = query.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return message


async def edit_message(
    message_id: int,
    payload: MessageEdit,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Message:
    message = await get_message(message_id, user, session)

    message.ai_response = payload.ai_response_edit
    await session.commit()
    await session.refresh(message)
    return message


async def send_message(
    message_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Message:
    try:
        message = await get_message(message_id, user, session)
        integration = message.integration

        if not message.ai_response:
            raise HTTPException(status_code=400, detail="AI response not generated")

        session_path = os.path.join("/code/sessions_dir", integration.session_file)
        decrypted_api_hash = encryption_service.decrypt(integration.telegram_api_hash)
        client = TelegramClient(session_path, integration.telegram_api_id, decrypted_api_hash)
        await client.connect()


        if not message.chat_id:
            raise HTTPException(
                status_code=400, 
                detail="Cannot send message: chat_id is not available. Message was saved without chat_id."
            )

        chan_id = message.channel_id

        entity = await client.get_entity(chan_id)

        input_peer = await client.get_input_entity(entity)
        full = await client(GetFullChannelRequest(channel=input_peer))
        linked = getattr(full.full_chat, 'linked_chat_id', None)

        resp = await client(
            GetDiscussionMessageRequest(peer=input_peer, msg_id=int(message.message_id))
        )
        disc_msg = resp.messages[0]
        target_chat = linked
        reply_to = disc_msg.id

        await client.send_message(
            entity=target_chat,
            message=message.ai_response,
            reply_to=reply_to
        )

        await client.disconnect()

        message.ai_response_sent = True
        message.ai_response_status = AIResponseStatus.SENT
        await session.commit()
        await session.refresh(message)
        return message
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send message: {str(e)}")


async def stats_by_message(
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[MessageStatsDaily]:
    q = await session.execute(
        select(MessageStatsDaily).where(MessageStatsDaily.user_id == user.id)
    )

    stats = q.scalars().all()

    return stats