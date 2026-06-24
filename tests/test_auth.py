from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import UserModel


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient,
    user: UserModel,
) -> None:
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "testpassword"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient,
    user: UserModel,
) -> None:
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "wrong"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "x"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient) -> None:
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_me_with_valid_token(
    client: AsyncClient,
    user: UserModel,
    auth_headers: dict,
) -> None:
    r = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["email"] == user.email
    assert body["role"] == user.role


@pytest.mark.asyncio
async def test_refresh_tokens(
    client: AsyncClient,
    user: UserModel,
) -> None:
    login_r = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "testpassword"},
    )
    refresh_token = login_r.json()["refresh_token"]

    r = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "access_token" in body
