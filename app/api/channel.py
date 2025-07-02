from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from app.models.monitored_channel import MonitoredChannel
from app.models.telegram_integration import TelegramIntegration
from app.models.subproject import Subproject
from app.models.project import Project
from app.core.jwt_utils import get_current_user_id
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.core.config import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class ChannelCreate(BaseModel):
    integration_id: int
    subproject_id: int
    channel_id: str
    channel_title: str = ""
    filters: dict = Field(default_factory=dict)
    is_active: bool = True

class ChannelOut(BaseModel):
    id: int
    user_id: int
    integration_id: int
    subproject_id: int
    channel_id: str
    channel_title: str | None
    filters: dict | None
    is_active: bool
    created_at: str
    class Config:
        orm_mode = True

router = APIRouter()

async def check_integration_owner(session, integration_id: int, user_id: int):
    q = await session.execute(select(TelegramIntegration).where(TelegramIntegration.id == integration_id, TelegramIntegration.user_id == user_id))
    integration = q.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=403, detail="Not allowed for this integration")
    return integration

async def check_subproject_owner(session, subproject_id: int, user_id: int):
    q = await session.execute(
        select(Subproject).join(Project).where(Subproject.id == subproject_id, Project.owner_id == user_id)
    )
    subproject = q.scalar_one_or_none()
    if not subproject:
        raise HTTPException(status_code=403, detail="Not allowed for this subproject")
    return subproject

@router.post("/channels", response_model=ChannelOut)
async def create_channel(data: ChannelCreate, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        await check_integration_owner(session, data.integration_id, user_id)
        await check_subproject_owner(session, data.subproject_id, user_id)
        channel = MonitoredChannel(
            user_id=user_id,
            integration_id=data.integration_id,
            subproject_id=data.subproject_id,
            channel_id=data.channel_id,
            channel_title=data.channel_title,
            filters=data.filters,
            is_active=data.is_active
        )
        session.add(channel)
        await session.commit()
        await session.refresh(channel)
        return channel

@router.get("/channels", response_model=list[ChannelOut])
async def list_channels(user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(MonitoredChannel).where(MonitoredChannel.user_id == user_id))
        return q.scalars().all()

@router.get("/channels/{channel_id}", response_model=ChannelOut)
async def get_channel(channel_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(MonitoredChannel).where(MonitoredChannel.id == channel_id, MonitoredChannel.user_id == user_id))
        channel = q.scalar_one_or_none()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        return channel

@router.patch("/channels/{channel_id}", response_model=ChannelOut)
async def update_channel(channel_id: int, data: ChannelCreate, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        await check_integration_owner(session, data.integration_id, user_id)
        await check_subproject_owner(session, data.subproject_id, user_id)
        q = await session.execute(select(MonitoredChannel).where(MonitoredChannel.id == channel_id, MonitoredChannel.user_id == user_id))
        channel = q.scalar_one_or_none()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        channel.integration_id = data.integration_id
        channel.subproject_id = data.subproject_id
        channel.channel_id = data.channel_id
        channel.channel_title = data.channel_title
        channel.filters = data.filters
        channel.is_active = data.is_active
        await session.commit()
        await session.refresh(channel)
        return channel

@router.delete("/channels/{channel_id}", status_code=204)
async def delete_channel(channel_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(MonitoredChannel).where(MonitoredChannel.id == channel_id, MonitoredChannel.user_id == user_id))
        channel = q.scalar_one_or_none()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        await session.delete(channel)
        await session.commit()
        return None

@router.get("/monitored_channels", response_model=list[ChannelOut])
async def list_monitored_channels(subproject_id: int = Query(None), user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(MonitoredChannel).where(MonitoredChannel.user_id == user_id))
        channels = q.scalars().all()
        if subproject_id:
            channels = [c for c in channels if c.subproject_id == subproject_id]
        return channels

@router.get("/monitored_channels/{channel_id}", response_model=ChannelOut)
async def get_monitored_channel(channel_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(MonitoredChannel).where(MonitoredChannel.id == channel_id, MonitoredChannel.user_id == user_id))
        channel = q.scalar_one_or_none()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        return channel

@router.patch("/monitored_channels/{channel_id}", response_model=ChannelOut)
async def patch_monitored_channel(channel_id: int, data: ChannelCreate, user_id: int = Depends(get_current_user_id)):
    # alias для PATCH /channels/{id}
    async with SessionLocal() as session:
        await check_integration_owner(session, data.integration_id, user_id)
        await check_subproject_owner(session, data.subproject_id, user_id)
        q = await session.execute(select(MonitoredChannel).where(MonitoredChannel.id == channel_id, MonitoredChannel.user_id == user_id))
        channel = q.scalar_one_or_none()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        channel.integration_id = data.integration_id
        channel.subproject_id = data.subproject_id
        channel.channel_id = data.channel_id
        channel.channel_title = data.channel_title
        channel.filters = data.filters
        channel.is_active = data.is_active
        await session.commit()
        await session.refresh(channel)
        return channel 