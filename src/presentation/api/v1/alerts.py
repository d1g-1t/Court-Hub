from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from src.application.dto import AlertResponse
from src.application.use_cases.crud import acknowledge_alert, list_alerts
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.get("/", response_model=list[AlertResponse])
async def list_all(
    auth: AuthDep,
    session: SessionDep,
    acknowledged: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[AlertResponse]:
    items = await list_alerts(
        tenant_id=auth.tenant_id,
        acknowledged=acknowledged,
        session=session,
        limit=limit,
        offset=offset,
    )
    return [AlertResponse.model_validate(a) for a in items]


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def ack(
    alert_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> AlertResponse:
    alert = await acknowledge_alert(
        alert_id,
        user_id=auth.user_id,
        session=session,
    )
    return AlertResponse.model_validate(alert)
