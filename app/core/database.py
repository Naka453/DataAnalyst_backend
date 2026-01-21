from __future__ import annotations

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"ssl": "require"},
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db