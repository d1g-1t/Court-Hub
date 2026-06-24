from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from src.application.dto import (
    BudgetEntryResponse,
    CreateBudgetEntryRequest,
    SpendAnalyticsResponse,
)
from src.application.use_cases.crud import (
    create_budget_entry,
    get_spend_analytics,
    list_matter_budget,
)
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.post(
    "/matters/{matter_id}",
    response_model=BudgetEntryResponse,
    status_code=201,
)
async def create_entry(
    matter_id: UUID,
    body: CreateBudgetEntryRequest,
    auth: AuthDep,
    session: SessionDep,
) -> BudgetEntryResponse:
    entry = await create_budget_entry(
        matter_id, body,
        tenant_id=auth.tenant_id, user_id=auth.user_id, session=session,
    )
    return BudgetEntryResponse.model_validate(entry)


@router.get("/matters/{matter_id}", response_model=list[BudgetEntryResponse])
async def list_entries(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[BudgetEntryResponse]:
    items = await list_matter_budget(
        matter_id, session=session, limit=limit, offset=offset,
    )
    return [BudgetEntryResponse.model_validate(e) for e in items]


@router.get("/matters/{matter_id}/spend", response_model=SpendAnalyticsResponse)
async def spend_analytics(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> SpendAnalyticsResponse:
    data = await get_spend_analytics(matter_id, session=session)
    return SpendAnalyticsResponse.model_validate(data)
