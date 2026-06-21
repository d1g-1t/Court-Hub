from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from src.domain.exceptions import AuthenticationError, NotFoundError
from src.infrastructure.database.repositories import UserSQLRepository


async def login(
    email: str,
    password: str,
    *,
    session: AsyncSession,
    settings: Settings,
) -> dict[str, str]:
    repo = UserSQLRepository(session)
    user = await repo.get_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthenticationError("Invalid email or password")
    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    access = create_access_token(user.id, user.role, user.tenant_id, settings)
    refresh = create_refresh_token(user.id, settings)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


async def refresh_tokens(
    refresh_token: str,
    *,
    session: AsyncSession,
    settings: Settings,
) -> dict[str, str]:
    try:
        payload = decode_token(refresh_token, settings)
    except Exception as exc:
        raise AuthenticationError(f"Invalid refresh token: {exc}") from exc

    if payload.get("type") != "refresh":
        raise AuthenticationError("Not a refresh token")

    user_id = UUID(payload["sub"])
    repo = UserSQLRepository(session)
    user = await repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise AuthenticationError("User not found or disabled")

    access = create_access_token(user.id, user.role, user.tenant_id, settings)
    new_refresh = create_refresh_token(user.id, settings)
    return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer"}


async def get_current_user(
    user_id: UUID,
    *,
    session: AsyncSession,
):
    repo = UserSQLRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user
