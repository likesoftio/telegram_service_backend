from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from app.core.config import settings
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.future import select
import hashlib
import hmac
import time
import jwt
from app.core.jwt_utils import create_access_token, create_refresh_token, decode_jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class TelegramAuthRequest(BaseModel):
    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    auth_date: int
    hash: str

    @classmethod
    def validate_auth_date(cls, v):
        now = int(datetime.now(timezone.utc).timestamp())
        if abs(now - v) > 86400:
            raise ValueError("auth_date is too old")
        return v

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield cls.validate_auth_date

    # остальные поля можно добавить при необходимости

def check_telegram_auth(data: dict, token: str) -> bool:
    auth_data = [f"{k}={v}" for k, v in sorted(data.items()) if k != "hash"]
    data_check_string = '\n'.join(auth_data)
    secret = hashlib.sha256(token.encode()).digest()
    h = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
    return h == data["hash"]

def create_jwt(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": int(time.time()) + 60 * 60 * 24 * 7  # 7 дней
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

router = APIRouter()

@router.post("/auth/telegram")
async def auth_telegram(payload: TelegramAuthRequest):
    # Проверка подписи Telegram
    if not check_telegram_auth(payload.dict(), settings.SECRET_KEY):
        raise HTTPException(status_code=401, detail="Invalid Telegram signature")
    async with SessionLocal() as session:
        q = await session.execute(select(User).where(User.telegram_id == str(payload.id)))
        user = q.scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=str(payload.id),
                username=payload.username,
                first_name=payload.first_name,
                last_name=payload.last_name,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/auth/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = decode_jwt(credentials.credentials, token_type="refresh")
    user_id = int(payload["sub"])
    access_token = create_access_token(user_id)
    return {"access_token": access_token, "token_type": "bearer"} 