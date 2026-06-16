from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest
from redis.asyncio import Redis

from src.presentation.deps import SessionDep, get_redis

router = APIRouter()


@router.get("/live")
async def liveness() -> dict:
    return {"status": "ok", "version": "0.1.0"}


@router.get("/ready")
async def readiness(
    session: SessionDep,
    redis: Redis = Depends(get_redis),
) -> dict:
    pg_ok = False
    redis_ok = False
    try:
        await session.execute(__import__("sqlalchemy").text("SELECT 1"))
        pg_ok = True
    except Exception:
        pass
    try:
        redis_ok = await redis.ping()
    except Exception:
        pass
    status = "ok" if (pg_ok and redis_ok) else "degraded"
    return {"status": status, "postgres": pg_ok, "redis": redis_ok}


@router.get("/metrics")
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type="text/plain; charset=utf-8")
