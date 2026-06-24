from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from tests.conftest import make_create_matter_payload


async def _create_matter(client: AsyncClient, headers: dict) -> str:
    r = await client.post(
        "/api/v1/matters/",
        json=make_create_matter_payload(title="Deadline Matter"),
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


def _future_dt(hours: int = 48) -> str:
    return (datetime.now(UTC) + timedelta(hours=hours)).isoformat()


@pytest.mark.asyncio
async def test_create_deadline(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    matter_id = await _create_matter(client, auth_headers)
    payload = {
        "deadline_type": "RESPONSE",
        "title": "File response",
        "due_at": _future_dt(72),
        "priority": "HIGH",
        "source": "manual",
    }
    r = await client.post(
        f"/api/v1/deadlines/matters/{matter_id}",
        json=payload,
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["title"] == "File response"
    assert body["status"] == "OPEN"
    assert body["priority"] == "HIGH"


@pytest.mark.asyncio
async def test_list_deadlines(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    matter_id = await _create_matter(client, auth_headers)
    for i in range(3):
        await client.post(
            f"/api/v1/deadlines/matters/{matter_id}",
            json={
                "deadline_type": "RESPONSE",
                "title": f"Deadline {i}",
                "due_at": _future_dt(24 * (i + 1)),
                "source": "manual",
            },
            headers=auth_headers,
        )

    r = await client.get(
        f"/api/v1/deadlines/matters/{matter_id}",
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert len(r.json()) >= 3


@pytest.mark.asyncio
async def test_complete_deadline(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    matter_id = await _create_matter(client, auth_headers)
    create_r = await client.post(
        f"/api/v1/deadlines/matters/{matter_id}",
        json={
            "deadline_type": "RESPONSE",
            "title": "To complete",
            "due_at": _future_dt(48),
            "source": "manual",
        },
        headers=auth_headers,
    )
    dl_id = create_r.json()["id"]

    r = await client.post(
        f"/api/v1/deadlines/{dl_id}/complete",
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_upcoming_deadlines_dashboard(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    r = await client.get(
        "/api/v1/deadlines/dashboard/upcoming",
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)
