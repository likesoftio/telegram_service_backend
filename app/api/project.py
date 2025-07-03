from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.models.project import Project
from app.core.jwt_utils import get_current_user_id
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.core.config import settings
from app.models.subproject import Subproject, SubprojectOut

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class ProjectCreate(BaseModel):
    name: str

class ProjectOut(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: str
    class Config:
        from_attributes = True

router = APIRouter()

@router.post("/projects", response_model=ProjectOut)
async def create_project(data: ProjectCreate, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        project = Project(name=data.name, owner_id=user_id)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

@router.get("/projects", response_model=list[ProjectOut])
async def list_projects(user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(Project).where(Project.owner_id == user_id))
        return q.scalars().all()

@router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(Project).where(Project.id == project_id, Project.owner_id == user_id))
        project = q.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

@router.patch("/projects/{project_id}", response_model=ProjectOut)
async def update_project(project_id: int, data: ProjectCreate, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(Project).where(Project.id == project_id, Project.owner_id == user_id))
        project = q.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project.name = data.name
        await session.commit()
        await session.refresh(project)
        return project

@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(select(Project).where(Project.id == project_id, Project.owner_id == user_id))
        project = q.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await session.delete(project)
        await session.commit()
        return None

@router.get("/projects/{project_id}/subprojects", response_model=list[SubprojectOut])
async def list_subprojects_for_project(project_id: int, user_id: int = Depends(get_current_user_id)):
    async with SessionLocal() as session:
        q = await session.execute(
            select(Subproject).join(Project).where(Subproject.project_id == project_id, Project.owner_id == user_id)
        )
        return q.scalars().all() 