from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.models.telegram_integration import TelegramIntegration
from app.core.jwt_utils import get_current_user_id
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.core.config import settings
import httpx

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class TelegramIntegrationCreate(BaseModel):
    type: str = Field(..., pattern="^(bot|mtproto)$")
    name: str
    bot_token: str | None = None
    phone_number: str | None = None

class TelegramIntegrationOut(BaseModel):
    id: int
    user_id: int
    type: str
    name: str
    bot_token: str | None
    phone_number: str | None
    is_active: bool
    created_at: str
    class Config:
        from_attributes = True

router = APIRouter()

async def check_bot_token(token: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/getMe"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.status_code == 200 and resp.json().get("ok")

@router.post("/telegram/integrations", response_model=TelegramIntegrationOut)
async def add_integration(data: TelegramIntegrationCreate, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        if data.type == "bot":
            if not data.bot_token:
                raise HTTPException(status_code=400, detail="bot_token required for type=bot")
            if not await check_bot_token(data.bot_token):
                raise HTTPException(status_code=400, detail="Invalid bot token")
        # Для MTProto здесь будет логика Telethon (заглушка)
        integration = TelegramIntegration(
            user_id=user_id,
            type=data.type,
            name=data.name,
            bot_token=data.bot_token,
            phone_number=data.phone_number,
        )
        session.add(integration)
        await session.commit()
        await session.refresh(integration)
        return integration

@router.get("/telegram/integrations", response_model=list[TelegramIntegrationOut])
async def list_integrations(user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(TelegramIntegration).where(TelegramIntegration.user_id == user_id))
        return q.scalars().all()

@router.get("/integrations", response_model=list[TelegramIntegrationOut])
async def list_integrations_alias(user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(TelegramIntegration).where(TelegramIntegration.user_id == user_id))
        return q.scalars().all()

@router.delete("/integrations/{integration_id}", status_code=204)
async def delete_integration_alias(integration_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(TelegramIntegration).where(TelegramIntegration.id == integration_id, TelegramIntegration.user_id == user_id))
        integration = q.scalar_one_or_none()
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        await session.delete(integration)
        await session.commit()
        return None
