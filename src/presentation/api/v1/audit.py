from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from src.application.dto import AuditEventResponse
from src.application.use_cases.analytics import get_audit_timeline
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.get("/matters/{matter_id}", response_model=list[AuditEventResponse])
async def audit_trail(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[AuditEventResponse]:
    items = await get_audit_timeline(
        matter_id=matter_id, session=session, limit=limit, offset=offset,
    )
    return [AuditEventResponse.model_validate(e) for e in items]
