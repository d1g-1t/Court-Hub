from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_create_matter_payload


async def _create_matter(client: AsyncClient, headers: dict) -> str:
    r = await client.post(
        "/api/v1/matters/",
        json=make_create_matter_payload(title="Evidence Matter"),
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


@pytest.mark.asyncio
async def test_upload_evidence(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    matter_id = await _create_matter(client, auth_headers)
    file_content = b"Fake contract content"
    r = await client.post(
        f"/api/v1/evidence/matters/{matter_id}",
        files={"file": ("contract.pdf", file_content, "application/pdf")},
        data={"evidence_type": "DOCUMENT", "privilege_level": "STANDARD"},
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["file_name"] == "contract.pdf"
    assert body["mime_type"] == "application/pdf"
    assert body["evidence_type"] == "DOCUMENT"


@pytest.mark.asyncio
async def test_list_evidence(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    matter_id = await _create_matter(client, auth_headers)
    for i, name in enumerate(["doc1.pdf", "doc2.txt"]):
        await client.post(
            f"/api/v1/evidence/matters/{matter_id}",
            files={"file": (name, b"content", "application/octet-stream")},
            data={"evidence_type": "DOCUMENT"},
            headers=auth_headers,
        )

    r = await client.get(
        f"/api/v1/evidence/matters/{matter_id}",
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    assert len(r.json()) >= 2


@pytest.mark.asyncio
async def test_get_evidence_not_found(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    r = await client.get(
        "/api/v1/evidence/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert r.status_code == 404
