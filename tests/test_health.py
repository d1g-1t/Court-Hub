from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient) -> None:
    r = await client.get("/api/v1/health/live")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness_structure(client: AsyncClient) -> None:
    r = await client.get("/api/v1/health/ready")
    assert r.status_code in (200, 503)
    body = r.json()
    assert "status" in body
