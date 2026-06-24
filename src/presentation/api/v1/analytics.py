from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from src.application.dto import (
    AuditEventResponse,
    DeadlineRiskResponse,
    PortfolioAnalyticsResponse,
)
from src.application.use_cases.analytics import (
    get_audit_timeline,
    get_cycle_time,
    get_deadline_risk,
    get_portfolio_analytics,
)
from src.presentation.deps import AuthDep, CacheDep, SessionDep

router = APIRouter()


@router.get("/portfolio", response_model=PortfolioAnalyticsResponse)
async def portfolio(
    auth: AuthDep,
    session: SessionDep,
    cache: CacheDep,
) -> PortfolioAnalyticsResponse:
    data = await get_portfolio_analytics(
        tenant_id=auth.tenant_id, session=session, cache=cache,
    )
    return PortfolioAnalyticsResponse.model_validate(data)


@router.get("/deadline-risk", response_model=DeadlineRiskResponse)
async def deadline_risk(
    auth: AuthDep,
    session: SessionDep,
    days: int = Query(7, ge=1, le=90),
) -> DeadlineRiskResponse:
    data = await get_deadline_risk(
        tenant_id=auth.tenant_id, session=session,
    )
    return DeadlineRiskResponse.model_validate(data)


@router.get("/cycle-time")
async def cycle_time(
    auth: AuthDep,
    session: SessionDep,
) -> dict:
    return await get_cycle_time(tenant_id=auth.tenant_id, session=session)


@router.get("/matters/{matter_id}/audit", response_model=list[AuditEventResponse])
async def audit_timeline(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[AuditEventResponse]:
    items = await get_audit_timeline(
        matter_id=matter_id, session=session, limit=limit, offset=offset,
    )
    return [AuditEventResponse.model_validate(e) for e in items]
