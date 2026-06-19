from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.application.dto import CreateMatterRequest
from src.core.config import Settings
from src.core.security import create_access_token, hash_password
from src.infrastructure.database.models import Base, TenantModel, UserModel
from src.presentation.deps import get_cache, get_db, get_redis, init_deps

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


class _FakeRedis:

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def get(self, key: str) -> bytes | None:
        val = self._store.get(key)
        return val

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        self._store[key] = value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def keys(self, pattern: str) -> list[str]:
        import fnmatch
        return [k for k in self._store if fnmatch.fnmatch(k, pattern)]

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        pass


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        app_env="test",
        postgres_host="localhost",
        postgres_port=5499,
        postgres_db="test",
        redis_host="localhost",
        redis_port=6399,
        paseto_secret_key="test-secret-key-exactly-32-bytes!",
    )


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(_TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(async_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest.fixture
def fake_redis() -> _FakeRedis:
    return _FakeRedis()


@pytest_asyncio.fixture
async def tenant(db_session: AsyncSession) -> TenantModel:
    t = TenantModel(
        id=uuid4(),
        name="Test Corp",
        slug=f"test-{uuid4().hex[:6]}",
    )
    db_session.add(t)
    await db_session.commit()
    await db_session.refresh(t)
    return t


@pytest_asyncio.fixture
async def user(db_session: AsyncSession, tenant: TenantModel) -> UserModel:
    u = UserModel(
        id=uuid4(),
        tenant_id=tenant.id,
        email=f"user-{uuid4().hex[:6]}@test.com",
        hashed_password=hash_password("testpassword"),
        role="admin",
    )
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u


@pytest.fixture
def auth_headers(user: UserModel, test_settings: Settings) -> dict[str, str]:
    token = create_access_token(user.id, user.role, user.tenant_id, test_settings)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def app(
    async_engine,
    fake_redis: _FakeRedis,
    test_settings: Settings,
) -> FastAPI:
    from src.infrastructure.cache.service import CacheService
    from src.main import create_app

    _app = create_app()

    factory = async_sessionmaker(async_engine, expire_on_commit=False)

    async def _get_db():
        async with factory() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    def _get_redis():
        return fake_redis

    def _get_cache():
        return CacheService(fake_redis)

    _app.dependency_overrides[get_db] = _get_db
    _app.dependency_overrides[get_redis] = _get_redis
    _app.dependency_overrides[get_cache] = _get_cache

    return _app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


def make_create_matter_payload(**overrides) -> dict:
    defaults = {
        "title": "Test Matter",
        "matter_type": "COMMERCIAL",
        "court_system": "ARBITRAZH",
        "role_in_case": "RESPONDENT",
        "risk_level": "MEDIUM",
    }
    defaults.update(overrides)
    return defaults
