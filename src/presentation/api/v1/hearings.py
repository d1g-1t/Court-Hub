from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from src.application.dto import (
    CreateHearingRequest,
    HearingOutcomeRequest,
    HearingResponse,
    UpdateHearingRequest,
)
from src.application.use_cases import hearings as hearing_uc
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.post("/matters/{matter_id}", response_model=HearingResponse, status_code=201)
async def create_hearing(
    matter_id: UUID,
    body: CreateHearingRequest,
    auth: AuthDep,
    session: SessionDep,
) -> HearingResponse:
    hearing = await hearing_uc.create_hearing(
        matter_id, body,
        tenant_id=auth.tenant_id, user_id=auth.user_id, session=session,
    )
    return HearingResponse.model_validate(hearing)


@router.get("/matters/{matter_id}", response_model=list[HearingResponse])
async def list_hearings(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> list[HearingResponse]:
    items = await hearing_uc.list_matter_hearings(matter_id, session=session)
    return [HearingResponse.model_validate(h) for h in items]


@router.patch("/{hearing_id}", response_model=HearingResponse)
async def update_hearing(
    hearing_id: UUID,
    body: UpdateHearingRequest,
    auth: AuthDep,
    session: SessionDep,
) -> HearingResponse:
    hearing = await hearing_uc.update_hearing(hearing_id, body, session=session)
    return HearingResponse.model_validate(hearing)


@router.post("/{hearing_id}/outcome", response_model=HearingResponse)
async def record_outcome(
    hearing_id: UUID,
    body: HearingOutcomeRequest,
    auth: AuthDep,
    session: SessionDep,
) -> HearingResponse:
    hearing = await hearing_uc.record_outcome(
        hearing_id, body.outcome_summary,
        tenant_id=auth.tenant_id, user_id=auth.user_id, session=session,
    )
    return HearingResponse.model_validate(hearing)
