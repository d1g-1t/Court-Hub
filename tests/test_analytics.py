from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_create_matter_payload


@pytest.mark.asyncio
async def test_portfolio_analytics(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    for i in range(2):
        await client.post(
            "/api/v1/matters/",
            json=make_create_matter_payload(title=f"Analytics Matter {i}"),
            headers=auth_headers,
        )

    r = await client.get(
        "/api/v1/analytics/portfolio",
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "total_matters" in body


@pytest.mark.asyncio
async def test_deadline_risk_dashboard(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    r = await client.get(
        "/api/v1/analytics/deadline-risk",
        headers=auth_headers,
        params={"days": 7},
    )
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_cycle_time(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    r = await client.get("/api/v1/analytics/cycle-time", headers=auth_headers)
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_audit_timeline(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    create_r = await client.post(
        "/api/v1/matters/",
        json=make_create_matter_payload(title="Audit Matter"),
        headers=auth_headers,
    )
    matter_id = create_r.json()["id"]

    r = await client.get(
        f"/api/v1/analytics/matters/{matter_id}/audit",
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)
