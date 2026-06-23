from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from src.application.dto import AssignOutsideCounselRequest, OutsideCounselResponse
from src.application.use_cases.crud import (
    assign_counsel,
    end_counsel_assignment,
    list_matter_counsel,
)
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.post(
    "/matters/{matter_id}/assign",
    response_model=OutsideCounselResponse,
    status_code=201,
)
async def assign(
    matter_id: UUID,
    body: AssignOutsideCounselRequest,
    auth: AuthDep,
    session: SessionDep,
) -> OutsideCounselResponse:
    assignment = await assign_counsel(
        matter_id, body,
        tenant_id=auth.tenant_id, user_id=auth.user_id, session=session,
    )
    return OutsideCounselResponse.model_validate(assignment)


@router.get("/matters/{matter_id}", response_model=list[OutsideCounselResponse])
async def list_counsel(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> list[OutsideCounselResponse]:
    items = await list_matter_counsel(matter_id, session=session)
    return [OutsideCounselResponse.model_validate(a) for a in items]


@router.post("/{assignment_id}/end", response_model=OutsideCounselResponse)
async def end_assignment(
    assignment_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> OutsideCounselResponse:
    assignment = await end_counsel_assignment(
        assignment_id,
        tenant_id=auth.tenant_id, user_id=auth.user_id, session=session,
    )
    return OutsideCounselResponse.model_validate(assignment)
