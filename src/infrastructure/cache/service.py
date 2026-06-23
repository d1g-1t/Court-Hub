"""Redis cache service — cache-aside pattern with TTL and invalidation."""

from __future__ import annotations

from typing import Any

import orjson
import structlog
from redis.asyncio import Redis

logger = structlog.get_logger(__name__)


class CacheService:
    """Thin wrapper over async Redis for structured cache operations."""

    def __init__(self, redis: Redis) -> None:
        self._r = redis

    async def get(self, key: str) -> Any | None:
        """Return deserialized value or None on miss."""
        raw = await self._r.get(key)
        if raw is None:
            return None
        try:
            return orjson.loads(raw)
        except orjson.JSONDecodeError:
            logger.warning("cache_decode_error", key=key)
            return None

    async def set(self, key: str, value: Any, *, ttl: int = 900) -> None:
        """Serialize and store with TTL in seconds."""
        await self._r.set(key, orjson.dumps(value), ex=ttl)

    async def delete(self, key: str) -> None:
        """Explicitly invalidate a key."""
        await self._r.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        """Invalidate all keys matching a glob pattern."""
        cursor: int = 0
        while True:
            cursor, keys = await self._r.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self._r.delete(*keys)
            if cursor == 0:
                break

    async def ping(self) -> bool:
        """Health check — returns True if Redis responds."""
        try:
            return await self._r.ping()  # type: ignore[return-value]
        except Exception:
            return False
