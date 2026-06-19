from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.config import Settings, get_settings
from src.core.security import decode_token
from src.infrastructure.cache.service import CacheService
from src.infrastructure.database.session import build_session_factory

_settings: Settings | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None
_redis: Redis | None = None


def init_deps(settings: Settings) -> None:
    global _settings, _session_factory, _redis
    _settings = settings
    _session_factory = build_session_factory(settings)
    _redis = Redis.from_url(settings.redis_url, decode_responses=False)


async def close_deps() -> None:
    global _redis, _session_factory
    if _redis:
        await _redis.aclose()
    if _session_factory:
        engine = _session_factory.kw.get("bind")
        if engine:
            await engine.dispose()


def get_app_settings() -> Settings:
    assert _settings is not None
    return _settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    assert _session_factory is not None
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_redis() -> Redis:
    assert _redis is not None
    return _redis


def get_cache(redis: Annotated[Redis, Depends(get_redis)]) -> CacheService:
    return CacheService(redis)


class TokenPayload:

    def __init__(self, user_id: UUID, role: str, tenant_id: UUID) -> None:
        self.user_id = user_id
        self.role = role
        self.tenant_id = tenant_id


async def get_current_user(
    authorization: Annotated[str, Header()],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> TokenPayload:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing Bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token, settings)
    except Exception as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc

    return TokenPayload(
        user_id=UUID(payload["sub"]),
        role=payload["role"],
        tenant_id=UUID(payload["tid"]),
    )


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CacheDep = Annotated[CacheService, Depends(get_cache)]
AuthDep = Annotated[TokenPayload, Depends(get_current_user)]
