from fastapi import (
    APIRouter,
    Depends,
    Form
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from collections.abc import Sequence

from src.core.database import get_async_session
from src.projects.api.v1.schemas import (
    ProjectRequest,
    ProjectResponse,
)
from src.projects.services.service import (
    create_project,
    get_list_owner_projects,
    get_project,
    update_project,
    delete_project,
)
from src.projects.models import Project
from src.accounts.services.dependencies import get_current_user
from src.accounts.models import User


router = APIRouter(
    prefix="/api/v1",
    tags=["projects"]
)


@router.post("/projects/", response_model=ProjectResponse)
async def create_project_router(
    payload: Annotated[ProjectRequest, Form()],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Project:
    project = await create_project(payload, user, session)

    return project


@router.get("/projects/", response_model=List[ProjectResponse])
async def list_projects_router(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[Project]:
    projects = await get_list_owner_projects(user, session)

    return projects


@router.get("/projects/{project_id}/", response_model=ProjectResponse)
async def get_project_router(
    project_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Project:
    projects = await get_project(project_id, user, session)

    return projects


@router.patch("/projects/{project_id}/", response_model=ProjectResponse)
async def update_project_router(
    project_id: int,
    payload: Annotated[ProjectRequest, Form()],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Project:
    project = await update_project(project_id, payload, user, session)

    return project


@router.delete("/projects/{project_id}/", status_code=204)
async def delete_project_router(
    project_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    await delete_project(project_id, user, session)
