from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Form
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.core.database import get_async_session
from src.accounts.api.v1.schemas import (
    UserWithTokensResponse,
    UserResponse,
    EmailRegisterRequest,
    UserUpdate,
    UserPasswordUpdate
)
from src.accounts.services.dependencies import get_current_user, create_access_token, create_refresh_token, decode_jwt
from src.accounts.services.service import (
    create_user,
    login_user,
    patch_me_alias,
    change_password
)
from src.accounts.models import User

router = APIRouter(
    prefix="/api/v1/user",
    tags=["user"]
)


@router.get("/", response_model=UserResponse)
async def get_me_router(
    user: User = Depends(get_current_user)
) -> User:
    return user


@router.post("/", response_model=UserWithTokensResponse)
async def create_user_router(
    payload: Annotated[EmailRegisterRequest, Form()],
    session: AsyncSession = Depends(get_async_session)
) -> UserWithTokensResponse:
    try:
        user = await create_user(payload, session)

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return UserWithTokensResponse(
            access=access_token,
            refresh=refresh_token,
            user=UserResponse.model_validate(user),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login/", response_model=UserWithTokensResponse)
async def login_user_router(
    payload: Annotated[EmailRegisterRequest, Form()],
    session: AsyncSession = Depends(get_async_session)
) -> UserWithTokensResponse:
    try:
        user = await login_user(payload, session)

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return UserWithTokensResponse(
            access=access_token,
            refresh=refresh_token,
            user=UserResponse.model_validate(user),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/", response_model=UserResponse)
async def patch_me_alias_router(
    payload: UserUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    user = await patch_me_alias(payload, user, session)

    return user


@router.patch("/pass/", response_model=UserResponse)
async def change_password_router(
    payload: UserPasswordUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    user = await change_password(payload, user, session)

    return user


@router.post("/refresh/", response_model=UserWithTokensResponse)
async def refresh_token_router(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    user: User = Depends(get_current_user),
) -> UserWithTokensResponse:
    try:
        payload = decode_jwt(credentials.credentials, token_type="refresh")
        user_id = int(payload["sub"])
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        return UserWithTokensResponse(
            access=access_token,
            refresh=refresh_token,
            user=UserResponse.model_validate(user),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
