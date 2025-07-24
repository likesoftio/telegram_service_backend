from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.settings import settings

DATABASE_URL = (f"postgresql+asyncpg://"
                f"{settings.POSTGRES_USER}:"
                f"{settings.POSTGRES_PASSWORD}@"
                f"{settings.POSTGRES_HOST}:"
                f"{settings.POSTGRES_PORT}/"
                f"{settings.POSTGRES_DB}")

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


sync_database_url = str(DATABASE_URL).replace("+asyncpg", "")
sync_engine = create_engine(sync_database_url)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)