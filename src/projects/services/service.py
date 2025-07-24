from fastapi import Depends, HTTPException
from collections.abc import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_async_session
from src.accounts.models import User
from src.projects.models import Project
from src.projects.api.v1.schemas import ProjectRequest


async def create_project(
    payload: ProjectRequest,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Project:
    project = Project(name=payload.name, user_id=user.id)

    session.add(project)
    await session.commit()
    await session.refresh(project)

    return project


async def get_list_owner_projects(
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[Project]:
    query = await session.execute(select(Project).where(Project.user_id == user.id))

    return query.scalars().all()


async def get_project(
    project_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Project:
    query = await session.execute(select(Project).where(Project.id == project_id, Project.user_id == user.id))

    project = query.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


async def update_project(
    project_id: int,
    payload: ProjectRequest,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> Project:
    project = await get_project(project_id, user, session)

    project.name = payload.name
    await session.commit()
    await session.refresh(project)

    return project


async def delete_project(
    project_id: int,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> None:
    project = await get_project(project_id, user, session)

    await session.delete(project)
    await session.commit()
    return None