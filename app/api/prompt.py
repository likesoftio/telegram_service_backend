from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from app.models.prompt_template import PromptTemplate
from app.models.prompt_settings_version import PromptSettingsVersion
from app.models.subproject import Subproject
from app.models.project import Project
from app.core.jwt_utils import get_current_user_id
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.core.config import settings
from sqlalchemy import func

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class PromptTemplateCreate(BaseModel):
    name: str
    description: str = ""
    subproject_id: int

class PromptTemplateOut(BaseModel):
    id: int
    name: str
    description: str
    subproject_id: int
    created_at: str
    class Config:
        orm_mode = True

class PromptSettingsVersionCreate(BaseModel):
    system_prompt: str
    params: dict = Field(default_factory=dict)

class PromptSettingsVersionOut(BaseModel):
    id: int
    prompt_template_id: int
    system_prompt: str
    params: dict | None
    version: int
    is_active: bool
    created_at: str
    class Config:
        orm_mode = True

router = APIRouter()

async def check_subproject_owner(session, subproject_id: int, user_id: int):
    q = await session.execute(
        select(Subproject).join(Project).where(Subproject.id == subproject_id, Project.owner_id == user_id)
    )
    subproject = q.scalar_one_or_none()
    if not subproject:
        raise HTTPException(status_code=403, detail="Not allowed for this subproject")
    return subproject

@router.post("/prompts", response_model=PromptTemplateOut)
async def create_prompt(data: PromptTemplateCreate, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        await check_subproject_owner(session, data.subproject_id, user_id)
        prompt = PromptTemplate(name=data.name, description=data.description, subproject_id=data.subproject_id)
        session.add(prompt)
        await session.commit()
        await session.refresh(prompt)
        return prompt

@router.get("/prompts", response_model=list[PromptTemplateOut])
async def list_prompts(user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(PromptTemplate).join(Subproject).join(Project).where(Project.owner_id == user_id)
        )
        return q.scalars().all()

@router.get("/prompts/{prompt_id}", response_model=PromptTemplateOut)
async def get_prompt(prompt_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(PromptTemplate).join(Subproject).join(Project).where(PromptTemplate.id == prompt_id, Project.owner_id == user_id)
        )
        prompt = q.scalar_one_or_none()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return prompt

@router.patch("/prompts/{prompt_id}", response_model=PromptTemplateOut)
async def update_prompt(prompt_id: int, data: PromptTemplateCreate, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        await check_subproject_owner(session, data.subproject_id, user_id)
        q = await session.execute(
            select(PromptTemplate).join(Subproject).join(Project).where(PromptTemplate.id == prompt_id, Project.owner_id == user_id)
        )
        prompt = q.scalar_one_or_none()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        prompt.name = data.name
        prompt.description = data.description
        prompt.subproject_id = data.subproject_id
        await session.commit()
        await session.refresh(prompt)
        return prompt

@router.delete("/prompts/{prompt_id}", status_code=204)
async def delete_prompt(prompt_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(PromptTemplate).join(Subproject).join(Project).where(PromptTemplate.id == prompt_id, Project.owner_id == user_id)
        )
        prompt = q.scalar_one_or_none()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        await session.delete(prompt)
        await session.commit()
        return None

# CRUD для версий настроек промпта
@router.get("/prompts/{prompt_id}/settings", response_model=list[PromptSettingsVersionOut])
async def list_prompt_settings(prompt_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        # Проверяем права
        q = await session.execute(
            select(PromptTemplate).join(Subproject).join(Project).where(PromptTemplate.id == prompt_id, Project.owner_id == user_id)
        )
        prompt = q.scalar_one_or_none()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        q2 = await session.execute(
            select(PromptSettingsVersion).where(PromptSettingsVersion.prompt_template_id == prompt_id)
        )
        return q2.scalars().all()

@router.post("/prompts/{prompt_id}/settings", response_model=PromptSettingsVersionOut)
async def create_prompt_settings(prompt_id: int, data: PromptSettingsVersionCreate, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        # Проверяем права
        q = await session.execute(
            select(PromptTemplate).join(Subproject).join(Project).where(PromptTemplate.id == prompt_id, Project.owner_id == user_id)
        )
        prompt = q.scalar_one_or_none()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        # Определяем версию
        q2 = await session.execute(
            select(func.max(PromptSettingsVersion.version)).where(PromptSettingsVersion.prompt_template_id == prompt_id)
        )
        max_version = q2.scalar() or 0
        version = max_version + 1
        settings_version = PromptSettingsVersion(
            prompt_template_id=prompt_id,
            system_prompt=data.system_prompt,
            params=data.params,
            version=version,
            is_active=False
        )
        session.add(settings_version)
        await session.commit()
        await session.refresh(settings_version)
        return settings_version

@router.post("/prompts/{prompt_id}/settings/{version}/activate", response_model=PromptSettingsVersionOut)
async def activate_prompt_settings(prompt_id: int, version: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        # Проверяем права
        q = await session.execute(
            select(PromptTemplate).join(Subproject).join(Project).where(PromptTemplate.id == prompt_id, Project.owner_id == user_id)
        )
        prompt = q.scalar_one_or_none()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        # Деактивируем все версии
        await session.execute(
            PromptSettingsVersion.__table__.update().where(PromptSettingsVersion.prompt_template_id == prompt_id).values(is_active=False)
        )
        # Активируем нужную версию
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

@router.get("/prompt_templates", response_model=list[PromptTemplateOut])
async def list_prompt_templates(subproject_id: int = Query(None), user_id: int = Depends(get_current_user_id)):
    # alias для /prompts
    async with SessionLocal() as session:
        q = await session.execute(
            select(PromptTemplate).join(Subproject).join(Project).where(Project.owner_id == user_id)
        )
        prompts = q.scalars().all()
        if subproject_id:
            prompts = [p for p in prompts if p.subproject_id == subproject_id]
        return prompts

@router.get("/prompt_templates/{prompt_id}", response_model=PromptTemplateOut)
async def get_prompt_template(prompt_id: int, user_id: int = Depends(get_current_user_id)):
    # alias для /prompts/{id}
    async with SessionLocal() as session:
        q = await session.execute(
            select(PromptTemplate).join(Subproject).join(Project).where(PromptTemplate.id == prompt_id, Project.owner_id == user_id)
        )
        prompt = q.scalar_one_or_none()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return prompt

@router.get("/prompt_settings_versions", response_model=list[PromptSettingsVersionOut])
async def list_prompt_settings_versions(prompt_template_id: int = Query(...), user_id: int = Depends(get_current_user_id)):
    # alias для /prompts/{prompt_id}/settings
    async with SessionLocal() as session:
        # Проверяем права
        q = await session.execute(
            select(PromptTemplate).join(Subproject).join(Project).where(PromptTemplate.id == prompt_template_id, Project.owner_id == user_id)
        )
        prompt = q.scalar_one_or_none()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        q2 = await session.execute(
            select(PromptSettingsVersion).where(PromptSettingsVersion.prompt_template_id == prompt_template_id)
        )
        return q2.scalars().all()
