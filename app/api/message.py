from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.models.message import Message
from app.models.subproject import Subproject
from app.models.project import Project
from app.core.jwt_utils import get_current_user_id
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.core.config import settings
from datetime import datetime

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class MessageOut(BaseModel):
    id: int
    user_id: int
    integration_id: int
    subproject_id: int
    channel_id: str
    channel_title: str | None
    message_id: str
    message_text: str
    message_date: str
    ai_response: str | None
    ai_response_status: str
    ai_response_edit: str | None
    ai_response_sent: bool
    prompt_template_id: int | None
    prompt_settings_version: int | None
    openai_model: str | None
    openai_token_usage: int | None
    openai_latency: float | None
    created_at: str
    class Config:
        orm_mode = True

class MessageEdit(BaseModel):
    ai_response_edit: str

router = APIRouter()

async def check_subproject_owner(session, subproject_id: int, user_id: int):
    q = await session.execute(
        select(Subproject).join(Project).where(Subproject.id == subproject_id, Project.owner_id == user_id)
    )
    subproject = q.scalar_one_or_none()
    if not subproject:
        raise HTTPException(status_code=403, detail="Not allowed for this subproject")
    return subproject

@router.get("/messages", response_model=list[MessageOut])
async def list_messages(status: str = "PENDING", user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Message).join(Subproject).join(Project)
            .where(Message.ai_response_status == status, Project.owner_id == user_id)
        )
        return q.scalars().all()

@router.post("/messages/{message_id}/approve", response_model=MessageOut)
async def approve_message(message_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Message).join(Subproject).join(Project)
            .where(Message.id == message_id, Project.owner_id == user_id)
        )
        msg = q.scalar_one_or_none()
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")
        msg.ai_response_status = "APPROVED"
        msg.ai_response_moderator_id = user_id
        msg.ai_response_moderation_time = datetime.utcnow()
        await session.commit()
        await session.refresh(msg)
        return msg

@router.post("/messages/{message_id}/decline", response_model=MessageOut)
async def decline_message(message_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Message).join(Subproject).join(Project)
            .where(Message.id == message_id, Project.owner_id == user_id)
        )
        msg = q.scalar_one_or_none()
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")
        msg.ai_response_status = "DECLINED"
        msg.ai_response_moderator_id = user_id
        msg.ai_response_moderation_time = datetime.utcnow()
        await session.commit()
        await session.refresh(msg)
        return msg

@router.patch("/messages/{message_id}", response_model=MessageOut)
async def edit_message(message_id: int, data: MessageEdit, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Message).join(Subproject).join(Project)
            .where(Message.id == message_id, Project.owner_id == user_id)
        )
        msg = q.scalar_one_or_none()
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")
        msg.ai_response_edit = data.ai_response_edit
        await session.commit()
        await session.refresh(msg)
        return msg

@router.post("/messages/{message_id}/send", response_model=MessageOut)
async def send_message(message_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Message).join(Subproject).join(Project)
            .where(Message.id == message_id, Project.owner_id == user_id)
        )
        msg = q.scalar_one_or_none()
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")
        # Здесь будет логика отправки в Telegram через интеграцию
        msg.ai_response_sent = True
        msg.ai_response_status = "SENT"
        await session.commit()
        await session.refresh(msg)
        return msg

@router.post("/messages/{message_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def like_message(message_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Message).join(Subproject).join(Project)
            .where(Message.id == message_id, Project.owner_id == user_id)
        )
        msg = q.scalar_one_or_none()
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")
        msg.liked_by_user = True
        await session.commit()
        return None

@router.post("/messages/{message_id}/unlike", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_message(message_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Message).join(Subproject).join(Project)
            .where(Message.id == message_id, Project.owner_id == user_id)
        )
        msg = q.scalar_one_or_none()
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")
        msg.liked_by_user = False
        await session.commit()
        return None 