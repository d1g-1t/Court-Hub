from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import orjson
import pyseto
from passlib.context import CryptContext
from pyseto import Key

from src.core.config import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _get_key(settings: Settings) -> Key:
    secret = settings.paseto_secret_key.encode("utf-8").ljust(32, b"\0")[:32]
    return Key.new(version=4, purpose="local", key=secret)


def create_access_token(
    user_id: UUID,
    role: str,
    tenant_id: UUID,
    settings: Settings,
) -> str:
    now = datetime.now(UTC)
    claims: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "tid": str(tenant_id),
        "iat": now.isoformat(),
        "exp": (now + timedelta(minutes=settings.access_token_ttl_minutes)).isoformat(),
        "type": "access",
    }
    key = _get_key(settings)
    token: bytes = pyseto.encode(key, payload=orjson.dumps(claims))
    return token.decode("utf-8")


def create_refresh_token(
    user_id: UUID,
    settings: Settings,
) -> str:
    now = datetime.now(UTC)
    claims: dict[str, Any] = {
        "sub": str(user_id),
        "iat": now.isoformat(),
        "exp": (now + timedelta(days=settings.refresh_token_ttl_days)).isoformat(),
        "type": "refresh",
    }
    key = _get_key(settings)
    token: bytes = pyseto.encode(key, payload=orjson.dumps(claims))
    return token.decode("utf-8")


def decode_token(token: str, settings: Settings) -> dict[str, Any]:
    key = _get_key(settings)
    decoded = pyseto.decode(key, token.encode("utf-8"))
    payload: dict[str, Any] = orjson.loads(decoded.payload)

    exp = datetime.fromisoformat(payload["exp"])
    if exp < datetime.now(UTC):
        raise ValueError("Token expired")

    return payload
