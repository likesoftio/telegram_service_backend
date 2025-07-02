from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.core.config import settings
from app.models.message_stats_daily import MessageStatsDaily
from app.core.jwt_utils import get_current_user_id

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

router = APIRouter()

@router.get("/stats/prompt/{prompt_id}")
async def stats_by_prompt(prompt_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(MessageStatsDaily).where(MessageStatsDaily.prompt_template_id == prompt_id)
        )
        return [row for row in q.scalars().all()]

@router.get("/stats/prompts/compare")
async def compare_prompt_versions(prompt_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(MessageStatsDaily).where(MessageStatsDaily.prompt_template_id == prompt_id)
        )
        stats = q.scalars().all()
        # Группируем по версии
        result = {}
        for s in stats:
            v = s.prompt_settings_version
            if v not in result:
                result[v] = []
            result[v].append(s)
        return result

@router.get("/stats/project/{project_id}")
async def stats_by_project(project_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        # Получаем все prompt_template_id проекта
        q = await session.execute(
            """
            SELECT id FROM prompt_templates WHERE subproject_id IN (
                SELECT id FROM subprojects WHERE project_id = :project_id
            )
            """,
            {"project_id": project_id}
        )
        prompt_ids = [row[0] for row in q.fetchall()]
        if not prompt_ids:
            return []
        q2 = await session.execute(
            select(MessageStatsDaily).where(MessageStatsDaily.prompt_template_id.in_(prompt_ids))
        )
        return [row for row in q2.scalars().all()]

@router.get("/stats/summary")
async def stats_summary(user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        # Получаем все prompt_template_id, принадлежащие проектам пользователя
        q = await session.execute(
            """
            SELECT pt.id FROM prompt_templates pt
            JOIN subprojects sp ON pt.subproject_id = sp.id
            JOIN projects p ON sp.project_id = p.id
            WHERE p.owner_id = :user_id
            """,
            {"user_id": user_id}
        )
        prompt_ids = [row[0] for row in q.fetchall()]
        if not prompt_ids:
            return {
                "messages_total": 0,
                "approved": 0,
                "declined": 0,
                "sent": 0,
                "liked_messages": 0,
                "avg_moderation_time": 0.0
            }
        q2 = await session.execute(
            select(MessageStatsDaily).where(MessageStatsDaily.prompt_template_id.in_(prompt_ids))
        )
        stats = q2.scalars().all()
        if not stats:
            return {
                "messages_total": 0,
                "approved": 0,
                "declined": 0,
                "sent": 0,
                "liked_messages": 0,
                "avg_moderation_time": 0.0
            }
        messages_total = sum(s.messages_total for s in stats)
        approved = sum(s.approved for s in stats)
        declined = sum(s.declined for s in stats)
        sent = sum(s.sent for s in stats)
        liked_messages = sum(s.liked_messages for s in stats)
        avg_moderation_time = (
            sum(s.avg_moderation_time for s in stats if s.avg_moderation_time) / max(1, len([s for s in stats if s.avg_moderation_time]))
        ) if any(s.avg_moderation_time for s in stats) else 0.0
        return {
            "messages_total": messages_total,
            "approved": approved,
            "declined": declined,
            "sent": sent,
            "liked_messages": liked_messages,
            "avg_moderation_time": avg_moderation_time
        } 