from __future__ import annotations

import secrets
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto import CreateMatterRequest, UpdateMatterRequest
from src.domain.exceptions import DuplicateError, NotFoundError
from src.domain.services import validate_matter_transition
from src.domain.value_objects import AuditEventType, MatterStatus
from src.infrastructure.cache.service import CacheService
from src.infrastructure.database.models import AuditEventModel, MatterModel
from src.infrastructure.database.repositories import (
    AuditSQLRepository,
    MatterSQLRepository,
)
from src.infrastructure.integrations.court_stub import KadStubAdapter, SudrfStubAdapter
from src.infrastructure.observability.metrics import MATTERS_TOTAL


def _generate_matter_number() -> str:
    return f"LCC-{secrets.token_hex(3).upper()}"


async def create_matter(
    data: CreateMatterRequest,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
    cache: CacheService,
) -> MatterModel:
    repo = MatterSQLRepository(session)
    matter_number = _generate_matter_number()

    while await repo.get_by_number(tenant_id, matter_number):
        matter_number = _generate_matter_number()

    matter = MatterModel(
        tenant_id=tenant_id,
        matter_number=matter_number,
        title=data.title,
        matter_type=data.matter_type,
        court_system=data.court_system,
        court_name=data.court_name,
        case_reference=data.case_reference,
        role_in_case=data.role_in_case,
        risk_level=data.risk_level,
        business_unit=data.business_unit,
        owner_user_id=user_id,
        estimated_exposure=data.estimated_exposure,
        currency=data.currency,
    )
    matter = await repo.create(matter)

    audit_repo = AuditSQLRepository(session)
    await audit_repo.create(
        AuditEventModel(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="matter",
            resource_id=matter.id,
            event_type=AuditEventType.CREATED.value,
            payload={"title": data.title, "matter_type": data.matter_type},
        )
    )

    MATTERS_TOTAL.labels(tenant_id=str(tenant_id), matter_type=data.matter_type).inc()
    await cache.delete_pattern("analytics:*")
    return matter


async def get_matter(
    matter_id: UUID,
    *,
    session: AsyncSession,
) -> MatterModel:
    repo = MatterSQLRepository(session)
    matter = await repo.get_by_id(matter_id)
    if not matter:
        raise NotFoundError("Matter", matter_id)
    return matter


async def list_matters(
    *,
    tenant_id: UUID,
    session: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
) -> list[MatterModel]:
    repo = MatterSQLRepository(session)
    if status:
        return await repo.list_by_status(tenant_id, status, limit=limit, offset=offset)
    return await repo.list_all(tenant_id=tenant_id, limit=limit, offset=offset)


async def update_matter(
    matter_id: UUID,
    data: UpdateMatterRequest,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
    cache: CacheService,
) -> MatterModel:
    repo = MatterSQLRepository(session)
    matter = await repo.get_by_id(matter_id)
    if not matter:
        raise NotFoundError("Matter", matter_id)

    old_status = matter.status

    update_data = data.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] != old_status:
        validate_matter_transition(
            MatterStatus(old_status), MatterStatus(update_data["status"])
        )

    for key, value in update_data.items():
        setattr(matter, key, value)
    matter.updated_at = datetime.now(UTC)

    matter = await repo.update(matter)

    audit_repo = AuditSQLRepository(session)
    event_type = (
        AuditEventType.STATUS_CHANGED
        if "status" in update_data
        else AuditEventType.UPDATED
    )
    await audit_repo.create(
        AuditEventModel(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="matter",
            resource_id=matter_id,
            event_type=event_type.value,
            payload=update_data,
        )
    )

    await cache.delete_pattern("analytics:*")
    return matter


async def close_matter(
    matter_id: UUID,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
    cache: CacheService,
) -> MatterModel:
    repo = MatterSQLRepository(session)
    matter = await repo.get_by_id(matter_id)
    if not matter:
        raise NotFoundError("Matter", matter_id)

    validate_matter_transition(MatterStatus(matter.status), MatterStatus.CLOSED)

    matter.status = MatterStatus.CLOSED
    matter.closed_at = datetime.now(UTC)
    matter.updated_at = datetime.now(UTC)
    matter = await repo.update(matter)

    audit_repo = AuditSQLRepository(session)
    await audit_repo.create(
        AuditEventModel(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="matter",
            resource_id=matter_id,
            event_type=AuditEventType.CLOSED.value,
        )
    )

    await cache.delete_pattern("analytics:*")
    return matter


async def import_from_court(
    case_reference: str,
    court_system: str,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
    cache: CacheService,
) -> MatterModel:
    if court_system == "ARBITRAZH":
        adapter = KadStubAdapter()
        case_data = await adapter.search_case(case_reference)
    else:
        adapter_sudrf = SudrfStubAdapter()
        case_data = await adapter_sudrf.search_case(case_reference)

    if not case_data:
        raise NotFoundError("CourtCase", case_reference)

    data = CreateMatterRequest(
        title=f"Дело {case_reference}",
        matter_type="CIVIL",
        court_system=court_system,
        court_name=case_data.get("court"),
        case_reference=case_reference,
        role_in_case="RESPONDENT",
    )
    return await create_matter(
        data, tenant_id=tenant_id, user_id=user_id, session=session, cache=cache
    )
