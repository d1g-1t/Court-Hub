from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from src.application.dto import CreateDeadlineRequest, DeadlineResponse, UpdateDeadlineRequest
from src.application.use_cases import deadlines as dl_uc
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.post("/matters/{matter_id}", response_model=DeadlineResponse, status_code=201)
async def create_deadline(
    matter_id: UUID,
    body: CreateDeadlineRequest,
    auth: AuthDep,
    session: SessionDep,
) -> DeadlineResponse:
    dl = await dl_uc.create_deadline(
        matter_id, body,
        tenant_id=auth.tenant_id, user_id=auth.user_id, session=session,
    )
    return DeadlineResponse.model_validate(dl)


@router.get("/matters/{matter_id}", response_model=list[DeadlineResponse])
async def list_deadlines(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> list[DeadlineResponse]:
    items = await dl_uc.list_matter_deadlines(matter_id, session=session)
    return [DeadlineResponse.model_validate(d) for d in items]


@router.patch("/{deadline_id}", response_model=DeadlineResponse)
async def update_deadline(
    deadline_id: UUID,
    body: UpdateDeadlineRequest,
    auth: AuthDep,
    session: SessionDep,
) -> DeadlineResponse:
    dl = await dl_uc.update_deadline(deadline_id, body, session=session)
    return DeadlineResponse.model_validate(dl)


@router.post("/{deadline_id}/complete", response_model=DeadlineResponse)
async def complete_deadline(
    deadline_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> DeadlineResponse:
    dl = await dl_uc.complete_deadline(
        deadline_id,
        tenant_id=auth.tenant_id, user_id=auth.user_id, session=session,
    )
    return DeadlineResponse.model_validate(dl)


@router.get("/dashboard/upcoming", response_model=list[DeadlineResponse])
async def upcoming_deadlines(
    auth: AuthDep,
    session: SessionDep,
    hours: int = Query(72, ge=1, le=720),
    limit: int = Query(50, ge=1, le=200),
) -> list[DeadlineResponse]:
    items = await dl_uc.get_upcoming_deadlines(
        tenant_id=auth.tenant_id, session=session, hours=hours, limit=limit
    )
    return [DeadlineResponse.model_validate(d) for d in items]


@router.get("/dashboard/overdue", response_model=list[DeadlineResponse])
async def overdue_deadlines(
    auth: AuthDep,
    session: SessionDep,
    limit: int = Query(50, ge=1, le=200),
) -> list[DeadlineResponse]:
    items = await dl_uc.get_overdue_deadlines(
        tenant_id=auth.tenant_id, session=session, limit=limit
    )
    return [DeadlineResponse.model_validate(d) for d in items]
