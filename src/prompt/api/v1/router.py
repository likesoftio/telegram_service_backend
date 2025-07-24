from fastapi import (
    APIRouter,
    Depends,
    Form,
    Query
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from collections.abc import Sequence

from src.core.database import get_async_session
from src.prompt.api.v1.schemas import (
    PromptTemplateRequest,
    PromptTemplateResponse,
    PromptTemplateUpdate,
    PromptSettingsVersionRequest,
    PromptSettingsVersionResponse,
    MessageResponse,
    MessageEdit,
    MessageAddTemp,
    MessageStatsResponse
)
from src.prompt.services.service import (
    create_prompt,
    list_prompts,
    get_prompt,
    update_prompt,
    delete_prompt,
    list_prompt_settings,
    create_prompt_settings,
    activate_prompt_settings,
    get_active_prompt_settings,
    get_prompt_settings_version,
    list_messages,
    send_message,
    add_prompt_template_for_message,
    edit_message,
    stats_by_message
)
from src.prompt.enums import AIResponseStatus
from src.prompt.models import PromptTemplate, PromptSettingsVersion, Message, MessageStatsDaily
from src.accounts.services.dependencies import get_current_user
from src.accounts.models import User


router = APIRouter(
    prefix="/api/v1",
    tags=["prompt"]
)


@router.post("/prompts/", response_model=PromptTemplateResponse)
async def create_prompt_router(
    payload: Annotated[PromptTemplateRequest, Form()],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> PromptTemplate:
    prompt = await create_prompt(payload, user, session)

    return prompt


@router.get("/prompts/", response_model=List[PromptTemplateResponse])
async def list_prompts_router(
    project_id: int = Query(None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[PromptTemplate]:
    prompts = await list_prompts(user, project_id, session)

    return prompts


@router.get("/prompts/{prompt_id}/", response_model=PromptTemplateResponse)
async def get_prompt_router(
    prompt_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> PromptTemplate:
    prompt = await get_prompt(prompt_id, user, session)

    return prompt


@router.patch("/prompts/{prompt_id}/", response_model=PromptTemplateResponse)
async def update_prompt_router(
    prompt_id: int,
    payload: PromptTemplateUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> PromptTemplate:
    prompt = await update_prompt(prompt_id, payload, user, session)
    return prompt


@router.delete("/prompts/{prompt_id}/", status_code=204)
async def delete_prompt_router(
    prompt_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    await delete_prompt(prompt_id, user, session)

    return None


@router.get("/prompts/{prompt_id}/settings/", response_model=List[PromptSettingsVersionResponse])
async def list_prompt_settings_router(
    prompt_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[PromptSettingsVersion]:
    prompts = await list_prompt_settings(prompt_id, user, session)

    return prompts


@router.get("/prompts/{prompt_id}/settings/is_active/", response_model=PromptSettingsVersionResponse)
async def get_active_prompt_settings_router(
    prompt_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> PromptSettingsVersion:
    settings = await get_active_prompt_settings(prompt_id, user, session)

    return settings


@router.get("/prompts/{prompt_id}/settings/{version}/", response_model=PromptSettingsVersionResponse)
async def get_prompt_settings_version_router(
    prompt_id: int,
    version: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> PromptSettingsVersion:
    settings = await get_prompt_settings_version(prompt_id, version, user, session)

    return settings


@router.post("/prompts/settings/", response_model=PromptSettingsVersionResponse)
async def create_prompt_settings_router(
    payload: PromptSettingsVersionRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> PromptSettingsVersion:
    settings_version = await create_prompt_settings(payload, user, session)

    return settings_version


@router.post("/prompts/{prompt_id}/settings/{version}/activate/", response_model=PromptSettingsVersionResponse)
async def activate_prompt_settings_router(
    prompt_id: int,
    version: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> PromptSettingsVersion:
    settings_version = await activate_prompt_settings(prompt_id, version, user, session)

    return settings_version


@router.get("/messages/", response_model=List[MessageResponse])
async def list_messages_router(
    status: AIResponseStatus = AIResponseStatus.PENDING,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[Message]:
    messages = await list_messages(user, status, session)

    return messages


@router.post("/messages/", response_model=MessageResponse)
async def add_prompt_template_for_message_router(
    payload: MessageAddTemp,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Message:
    messages = await add_prompt_template_for_message(payload, user, session)

    return messages


@router.patch("/messages/{message_id}/", response_model=MessageResponse)
async def edit_message_router(
    message_id: int,
    payload: MessageEdit,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Message:
    message = await edit_message(message_id, payload, user, session)

    return message


@router.post("/messages/{message_id}/send/", response_model=MessageResponse)
async def send_message_router(
    message_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Message:
    message = await send_message(message_id, user, session)

    return message


@router.get("/messages/stats/", response_model=List[MessageStatsResponse])
async def stats_by_message_router(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[MessageStatsDaily]:
    stats = await stats_by_message(user, session)

    return stats