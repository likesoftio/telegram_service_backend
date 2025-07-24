from fastapi import (
    APIRouter,
    Depends,
    Form
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from collections.abc import Sequence

from src.core.database import get_async_session
from src.telegram.api.v1.schemas import (
    TelegramIntegrationResponse,
    ChannelRequest,
    ChannelResponse,
    ChannelUpdateRequest,
    MTProtoRequest,
    ConfirmCodeRequest,
    MTProtoResponse
)
from src.telegram.services.service import (
    list_alies_integrations,
    get_alies_integrations,
    delete_alies_integrations,
    create_channel,
    list_alies_channels,
    get_alies_channel,
    update_channel,
    delete_channel,
    create_mtproto_integration,
    confirm_mtproto_code,
    get_channels_for_integration,
    get_channels_for_project
)
from src.telegram.models import TelegramIntegration, MonitoredChannel
from src.accounts.services.dependencies import get_current_user
from src.accounts.models import User


router = APIRouter(
    prefix="/api/v1",
    tags=["telegram"]
)


@router.post("/integrations/mtproto/", response_model=MTProtoResponse)
async def create_mtproto_integration_router(
    payload: Annotated[MTProtoRequest, Form()],
    user: User = Depends(get_current_user),
) -> MTProtoResponse:
    return await create_mtproto_integration(payload, user)


@router.post("/integrations/mtproto/confirm/", response_model=TelegramIntegrationResponse)
async def confirm_mtproto_code_router(
    payload: Annotated[ConfirmCodeRequest, Form()],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> TelegramIntegration:
    integration = await confirm_mtproto_code(payload, user, session)

    return integration


@router.get("/integrations/", response_model=List[TelegramIntegrationResponse])
async def list_alies_integrations_router(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[TelegramIntegration]:
    integrations = await list_alies_integrations(user, session)

    return integrations


@router.get("/integrations/{integration_id}/", response_model=TelegramIntegrationResponse)
async def get_alies_integrations_router(
    integration_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> TelegramIntegration:
    integrations = await get_alies_integrations(integration_id, user, session)

    return integrations


@router.delete("/integrations/{integration_id}/", status_code=204)
async def delete_integration_alias(
    integration_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    await delete_alies_integrations(integration_id, user, session)


@router.post("/channels/", response_model=ChannelResponse)
async def create_channel_router(
    payload: Annotated[ChannelRequest, Form()],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> MonitoredChannel:
    channel = await create_channel(payload, user, session)
    return channel


@router.get("/channels/", response_model=List[ChannelResponse])
async def list_channels_router(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[MonitoredChannel]:
    channels = await list_alies_channels(user, session)

    return channels


@router.get("/channels/{channel_id}/", response_model=ChannelResponse)
async def get_channel_router(
    channel_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> MonitoredChannel:
    channel = await get_alies_channel(channel_id, user, session)

    return channel


@router.get("/channels/integration/{integration_id}/", response_model=List[ChannelResponse])
async def get_channels_for_integration_router(
    integration_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[MonitoredChannel]:
    channel = await get_channels_for_integration(integration_id, user, session)

    return channel


@router.get("/channels/project/{project_id}/", response_model=List[ChannelResponse])
async def get_channels_for_integration_router(
    project_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[MonitoredChannel]:
    channel = await get_channels_for_project(project_id, user, session)

    return channel


@router.patch("/channels/{channel_id}/", response_model=ChannelResponse)
async def update_channel_router(
    channel_id: int,
    payload: ChannelUpdateRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> MonitoredChannel:
    channel = await update_channel(channel_id, payload, user, session)

    return channel


@router.delete("/channels/{channel_id}/", status_code=204)
async def delete_channel_router(
    channel_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    return await delete_channel(channel_id, user, session)