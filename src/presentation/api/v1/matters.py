from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from src.application.dto import (
    CreateMatterRequest,
    ImportFromCourtRequest,
    MatterResponse,
    UpdateMatterRequest,
)
from src.application.use_cases import matters as matter_uc
from src.presentation.deps import AuthDep, CacheDep, SessionDep

router = APIRouter()


@router.post("/", response_model=MatterResponse, status_code=201)
async def create_matter(
    body: CreateMatterRequest,
    auth: AuthDep,
    session: SessionDep,
    cache: CacheDep,
) -> MatterResponse:
    matter = await matter_uc.create_matter(
        body, tenant_id=auth.tenant_id, user_id=auth.user_id, session=session, cache=cache
    )
    return MatterResponse.model_validate(matter)


@router.get("/", response_model=list[MatterResponse])
async def list_matters(
    auth: AuthDep,
    session: SessionDep,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: str | None = None,
) -> list[MatterResponse]:
    matters = await matter_uc.list_matters(
        tenant_id=auth.tenant_id, session=session, limit=limit, offset=offset, status=status
    )
    return [MatterResponse.model_validate(m) for m in matters]


@router.get("/{matter_id}", response_model=MatterResponse)
async def get_matter(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> MatterResponse:
    matter = await matter_uc.get_matter(matter_id, session=session)
    return MatterResponse.model_validate(matter)


@router.patch("/{matter_id}", response_model=MatterResponse)
async def update_matter(
    matter_id: UUID,
    body: UpdateMatterRequest,
    auth: AuthDep,
    session: SessionDep,
    cache: CacheDep,
) -> MatterResponse:
    matter = await matter_uc.update_matter(
        matter_id, body,
        tenant_id=auth.tenant_id, user_id=auth.user_id,
        session=session, cache=cache,
    )
    return MatterResponse.model_validate(matter)


@router.post("/{matter_id}/close", response_model=MatterResponse)
async def close_matter(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
    cache: CacheDep,
) -> MatterResponse:
    matter = await matter_uc.close_matter(
        matter_id,
        tenant_id=auth.tenant_id, user_id=auth.user_id,
        session=session, cache=cache,
    )
    return MatterResponse.model_validate(matter)


@router.post("/import-from-court", response_model=MatterResponse, status_code=201)
async def import_from_court(
    body: ImportFromCourtRequest,
    auth: AuthDep,
    session: SessionDep,
    cache: CacheDep,
) -> MatterResponse:
    matter = await matter_uc.import_from_court(
        body.case_reference, body.court_system,
        tenant_id=auth.tenant_id, user_id=auth.user_id,
        session=session, cache=cache,
    )
    return MatterResponse.model_validate(matter)
