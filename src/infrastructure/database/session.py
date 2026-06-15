from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import Settings


def build_engine(settings: Settings):
    return create_async_engine(
        settings.database_url,
        echo=settings.app_env == "dev",
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
    )


def build_session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    engine = build_engine(settings)
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
