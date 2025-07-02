from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.models.subproject import Subproject
from app.models.project import Project
from app.core.jwt_utils import get_current_user_id
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.core.config import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class SubprojectCreate(BaseModel):
    name: str
    project_id: int

class SubprojectOut(BaseModel):
    id: int
    name: str
    project_id: int
    created_at: str
    class Config:
        orm_mode = True

router = APIRouter()

async def check_project_owner(session, project_id: int, user_id: int):
    q = await session.execute(select(Project).where(Project.id == project_id, Project.owner_id == user_id))
    project = q.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=403, detail="Not allowed for this project")
    return project

@router.post("/subprojects", response_model=SubprojectOut)
async def create_subproject(data: SubprojectCreate, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        await check_project_owner(session, data.project_id, user_id)
        subproject = Subproject(name=data.name, project_id=data.project_id)
        session.add(subproject)
        await session.commit()
        await session.refresh(subproject)
        return subproject

@router.get("/subprojects", response_model=list[SubprojectOut])
async def list_subprojects(user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        # Получаем только подпроекты, где пользователь владелец проекта
        q = await session.execute(
            select(Subproject).join(Project).where(Project.owner_id == user_id)
        )
        return q.scalars().all()

@router.get("/subprojects/{subproject_id}", response_model=SubprojectOut)
async def get_subproject(subproject_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Subproject).join(Project).where(Subproject.id == subproject_id, Project.owner_id == user_id)
        )
        subproject = q.scalar_one_or_none()
        if not subproject:
            raise HTTPException(status_code=404, detail="Subproject not found")
        return subproject

@router.patch("/subprojects/{subproject_id}", response_model=SubprojectOut)
async def update_subproject(subproject_id: int, data: SubprojectCreate, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        # Проверяем права на проект, к которому будет относиться подпроект
        await check_project_owner(session, data.project_id, user_id)
        q = await session.execute(
            select(Subproject).join(Project).where(Subproject.id == subproject_id, Project.owner_id == user_id)
        )
        subproject = q.scalar_one_or_none()
        if not subproject:
            raise HTTPException(status_code=404, detail="Subproject not found")
        subproject.name = data.name
        subproject.project_id = data.project_id
        await session.commit()
        await session.refresh(subproject)
        return subproject

@router.delete("/subprojects/{subproject_id}", status_code=204)
async def delete_subproject(subproject_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Subproject).join(Project).where(Subproject.id == subproject_id, Project.owner_id == user_id)
        )
        subproject = q.scalar_one_or_none()
        if not subproject:
            raise HTTPException(status_code=404, detail="Subproject not found")
        await session.delete(subproject)
        await session.commit()
        return None 