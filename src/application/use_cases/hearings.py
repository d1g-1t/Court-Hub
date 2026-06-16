from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto import CreateHearingRequest, UpdateHearingRequest
from src.domain.exceptions import NotFoundError
from src.domain.services import build_audit_event
from src.domain.value_objects import AuditEventType, HearingStatus
from src.infrastructure.database.models import HearingModel
from src.infrastructure.database.repositories import (
    AuditSQLRepository,
    HearingSQLRepository,
    MatterSQLRepository,
)


async def create_hearing(
    matter_id: UUID,
    data: CreateHearingRequest,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> HearingModel:
    matter_repo = MatterSQLRepository(session)
    if not await matter_repo.get_by_id(matter_id):
        raise NotFoundError("Matter", matter_id)

    repo = HearingSQLRepository(session)
    hearing = HearingModel(
        matter_id=matter_id,
        hearing_type=data.hearing_type,
        scheduled_at=data.scheduled_at,
        courtroom=data.courtroom,
        judge_name=data.judge_name,
    )
    hearing = await repo.create(hearing)

    audit_repo = AuditSQLRepository(session)
    await audit_repo.create(
        build_audit_event(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="hearing",
            resource_id=hearing.id,
            event_type=AuditEventType.CREATED,
            payload={"hearing_type": data.hearing_type},
        )
    )
    return hearing


async def list_matter_hearings(
    matter_id: UUID,
    *,
    session: AsyncSession,
) -> list[HearingModel]:
    repo = HearingSQLRepository(session)
    return await repo.list_by_matter(matter_id)


async def update_hearing(
    hearing_id: UUID,
    data: UpdateHearingRequest,
    *,
    session: AsyncSession,
) -> HearingModel:
    repo = HearingSQLRepository(session)
    hearing = await repo.get_by_id(hearing_id)
    if not hearing:
        raise NotFoundError("Hearing", hearing_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(hearing, key, value)
    return await repo.update(hearing)


async def record_outcome(
    hearing_id: UUID,
    outcome_summary: str,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> HearingModel:
    repo = HearingSQLRepository(session)
    hearing = await repo.get_by_id(hearing_id)
    if not hearing:
        raise NotFoundError("Hearing", hearing_id)

    hearing.status = HearingStatus.COMPLETED
    hearing.outcome_summary = outcome_summary
    hearing = await repo.update(hearing)

    audit_repo = AuditSQLRepository(session)
    await audit_repo.create(
        build_audit_event(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="hearing",
            resource_id=hearing_id,
            event_type=AuditEventType.STATUS_CHANGED,
            payload={"status": "COMPLETED", "outcome_summary": outcome_summary},
        )
    )
    return hearing
