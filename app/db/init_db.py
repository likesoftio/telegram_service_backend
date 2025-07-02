import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.base import Base
import app.models.user  # импортируем модель, чтобы она попала в metadata
import app.models.project
import app.models.subproject
import app.models.prompt_template
import app.models.prompt_settings_version
import app.models.telegram_integration
import app.models.monitored_channel
import app.models.message
import app.models.message_stats_daily

DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL, echo=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created!")

if __name__ == "__main__":
    asyncio.run(init_db()) 