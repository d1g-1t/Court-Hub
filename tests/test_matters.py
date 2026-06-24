from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_create_matter_payload


@pytest.mark.asyncio
async def test_create_matter(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    payload = make_create_matter_payload(title="Alpha Dispute")
    r = await client.post("/api/v1/matters/", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["title"] == "Alpha Dispute"
    assert body["status"] == "OPEN"
    assert body["matter_number"].startswith("LCC-")


@pytest.mark.asyncio
async def test_create_matter_requires_auth(client: AsyncClient) -> None:
    r = await client.post("/api/v1/matters/", json=make_create_matter_payload())
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_list_matters(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    for i in range(2):
        await client.post(
            "/api/v1/matters/",
            json=make_create_matter_payload(title=f"Matter {i}"),
            headers=auth_headers,
        )

    r = await client.get("/api/v1/matters/", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 2


@pytest.mark.asyncio
async def test_get_matter(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    create_r = await client.post(
        "/api/v1/matters/",
        json=make_create_matter_payload(title="Beta Case"),
        headers=auth_headers,
    )
    matter_id = create_r.json()["id"]

    r = await client.get(f"/api/v1/matters/{matter_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["id"] == matter_id


@pytest.mark.asyncio
async def test_get_matter_not_found(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    r = await client.get(
        "/api/v1/matters/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_matter(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    create_r = await client.post(
        "/api/v1/matters/",
        json=make_create_matter_payload(title="Gamma LLC"),
        headers=auth_headers,
    )
    matter_id = create_r.json()["id"]

    r = await client.patch(
        f"/api/v1/matters/{matter_id}",
        json={"title": "Gamma LLC (updated)", "risk_level": "HIGH"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Gamma LLC (updated)"
    assert r.json()["risk_level"] == "HIGH"


@pytest.mark.asyncio
async def test_close_matter(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    create_r = await client.post(
        "/api/v1/matters/",
        json=make_create_matter_payload(title="Short Case"),
        headers=auth_headers,
    )
    matter_id = create_r.json()["id"]

    r = await client.post(
        f"/api/v1/matters/{matter_id}/close",
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "CLOSED"
