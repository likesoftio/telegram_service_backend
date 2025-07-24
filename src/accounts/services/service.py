from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.hash import bcrypt

from src.core.database import get_async_session
from src.accounts.models import User
from src.accounts.services.dependencies import pwd_context
from src.accounts.api.v1.schemas import EmailRegisterRequest, UserUpdate, UserPasswordUpdate


async def create_user(
    payload: EmailRegisterRequest,
    session: AsyncSession = Depends(get_async_session)
) -> User:
    existing_user = await session.execute(select(User).where(User.email == payload.email))

    user = existing_user.scalar_one_or_none()

    if user:
        raise ValueError(f"User with email {payload.email} already exists")

    user = User(
        email=payload.email,
        password_hash=pwd_context.hash(payload.password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def login_user(
    payload: EmailRegisterRequest,
    session: AsyncSession = Depends(get_async_session)
) -> User:
    existing_user = await session.execute(select(User).where(User.email == payload.email))

    user = existing_user.scalar_one_or_none()

    if not user:
        raise ValueError(f"User with email {payload.email} not exists")

    if not user.password_hash or not bcrypt.verify(payload.password, user.password_hash):
        raise ValueError("Invalid email or password")

    return user


async def patch_me_alias(
    payload: UserUpdate,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> User:
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(user, field, value)

    await session.commit()
    await session.refresh(user)

    return user


async def change_password(
    payload: UserPasswordUpdate,
    user: User,
    session: AsyncSession = Depends(get_async_session)
) -> User:
    if not user.password_hash or not bcrypt.verify(payload.old_password, user.password_hash):
        raise ValueError("Invalid password")

    if payload.old_password == payload.new_password:
        raise ValueError("New password must be different from old password")

    user.password_hash = pwd_context.hash(payload.new_password)
    await session.commit()
    await session.refresh(user)
    return user