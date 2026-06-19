from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from src.application.dto import ClaimResponse, CreateClaimRequest
from src.application.use_cases.crud import create_claim, list_matter_claims
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.post("/matters/{matter_id}", response_model=ClaimResponse, status_code=201)
async def create(
    matter_id: UUID,
    body: CreateClaimRequest,
    auth: AuthDep,
    session: SessionDep,
) -> ClaimResponse:
    claim = await create_claim(matter_id, body, session=session)
    return ClaimResponse.model_validate(claim)


@router.get("/matters/{matter_id}", response_model=list[ClaimResponse])
async def list_claims(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> list[ClaimResponse]:
    items = await list_matter_claims(matter_id, session=session)
    return [ClaimResponse.model_validate(c) for c in items]
