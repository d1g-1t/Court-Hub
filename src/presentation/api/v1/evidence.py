from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, UploadFile

from src.application.dto import EvidenceResponse, EvidenceUploadMeta
from src.application.use_cases.crud import (
    get_evidence,
    list_matter_evidence,
    upload_evidence,
)
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.post("/matters/{matter_id}", response_model=EvidenceResponse, status_code=201)
async def upload(
    matter_id: UUID,
    file: UploadFile,
    auth: AuthDep,
    session: SessionDep,
    evidence_type: str = "DOCUMENT",
    privilege_level: str = "STANDARD",
) -> EvidenceResponse:
    content = await file.read()
    meta = EvidenceUploadMeta(evidence_type=evidence_type, privilege_level=privilege_level)
    ev = await upload_evidence(
        matter_id,
        file.filename or "unnamed",
        file.content_type or "application/octet-stream",
        content,
        meta,
        tenant_id=auth.tenant_id,
        user_id=auth.user_id,
        session=session,
    )
    return EvidenceResponse.model_validate(ev)


@router.get("/matters/{matter_id}", response_model=list[EvidenceResponse])
async def list_evidence(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> list[EvidenceResponse]:
    items = await list_matter_evidence(matter_id, session=session)
    return [EvidenceResponse.model_validate(e) for e in items]


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence_item(
    evidence_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> EvidenceResponse:
    ev = await get_evidence(evidence_id, session=session)
    return EvidenceResponse.model_validate(ev)
