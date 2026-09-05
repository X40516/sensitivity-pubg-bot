"""
Database engine va session factory.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


def _to_async_dsn(dsn: str) -> str:
    """postgresql:// -> postgresql+asyncpg:// ga o'giradi, agar kerak bo'lsa."""
    if dsn.startswith("postgresql+asyncpg://"):
        return dsn
    if dsn.startswith("postgresql://"):
        return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
    if dsn.startswith("postgres://"):
        return dsn.replace("postgres://", "postgresql+asyncpg://", 1)
    return dsn


engine = create_async_engine(_to_async_dsn(settings.database_url), pool_pre_ping=True, future=True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_models() -> None:
    """Ishlab chiqishda tez boshlash uchun (productionda Alembic migratsiyalarini ishlating)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
