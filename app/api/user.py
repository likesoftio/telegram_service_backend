from fastapi import APIRouter, Depends, Body, HTTPException
from app.core.jwt_utils import get_current_user_id
from app.models.user import User
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.core.config import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

router = APIRouter()

@router.get("/me")
async def get_me(user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(User).where(User.id == user_id))
        user = q.scalar_one_or_none()
        if not user:
            return {"detail": "User not found"}
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }

@router.get("/users/me")
async def get_me_alias(user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(User).where(User.id == user_id))
        user = q.scalar_one_or_none()
        if not user:
            return {"detail": "User not found"}
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "full_name": getattr(user, "full_name", None),
            "email": getattr(user, "email", None),
            "language": getattr(user, "language", None),
        }

@router.patch("/users/me")
async def patch_me_alias(
    data: dict = Body(...),
    user_id: int = Depends(get_current_user_id)
):
    async with SessionLocal() as session:
        q = await session.execute(select(User).where(User.id == user_id))
        user = q.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        for field in ["full_name", "email", "language"]:
            if field in data:
                setattr(user, field, data[field])
        await session.commit()
        await session.refresh(user)
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "full_name": getattr(user, "full_name", None),
            "email": getattr(user, "email", None),
            "language": getattr(user, "language", None),
        } 