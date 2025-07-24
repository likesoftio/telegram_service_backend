from fastapi import APIRouter, Query, Depends
from typing import Dict
from loguru import logger
from sqlalchemy import select   
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.prompt.enums import AIResponseStatus
from src.prompt.models import Message
from src.accounts.services.dependencies import get_current_user
from src.accounts.models import User
from src.ai_task.tasks import scan_channels_task, generate_ai_response_task, aggregate_user_stats_today


router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["tasks"]
)


@router.post("/scan_channels/")
async def run_scan_channels(user_id: int = Query(None)) -> Dict[str, str]:
    scan_channels_task.delay(user_id)
    return {"status": "started"}


@router.post("/generate_ai_response/{message_id}/")
async def run_generate_ai_response(
    message_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Dict[str, str]:
    q = await session.execute(select(Message).where(Message.id == message_id, Message.user_id == user.id))
    msg = q.scalar_one_or_none()
    
    if not msg:
        logger.error(f"Message {message_id} not found")
        return "Message not found"
    
    # Проверяем, есть ли prompt_template_id
    if not msg.prompt_template_id:
        logger.error(f"Message {message_id} has no prompt_template_id")
        return "No prompt template assigned"

    msg.ai_response_status = AIResponseStatus.PENDING
    await session.commit()
    generate_ai_response_task.delay(message_id, user.id)
    return {"status": "started"}


@router.post("/aggregate_user_stats_today/{user_id}/")
async def run_aggregate_user_stats_today(
    user_id: int,
) -> Dict[str, str]:
    aggregate_user_stats_today.delay(user_id)
    return {"status": "started"}