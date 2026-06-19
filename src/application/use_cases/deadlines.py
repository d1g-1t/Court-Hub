from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto import CreateDeadlineRequest, UpdateDeadlineRequest
from src.domain.exceptions import NotFoundError
from src.domain.services import build_audit_event, evaluate_deadline_risk
from src.domain.value_objects import AuditEventType, DeadlineStatus
from src.domain.entities import ProceduralDeadline
from src.infrastructure.database.models import AlertModel, DeadlineModel
from src.infrastructure.database.repositories import (
    AlertSQLRepository,
    AuditSQLRepository,
    DeadlineSQLRepository,
    MatterSQLRepository,
)


async def create_deadline(
    matter_id: UUID,
    data: CreateDeadlineRequest,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> DeadlineModel:
    matter_repo = MatterSQLRepository(session)
    matter = await matter_repo.get_by_id(matter_id)
    if not matter:
        raise NotFoundError("Matter", matter_id)

    repo = DeadlineSQLRepository(session)
    deadline = DeadlineModel(
        matter_id=matter_id,
        deadline_type=data.deadline_type,
        title=data.title,
        due_at=data.due_at,
        priority=data.priority,
        assigned_user_id=data.assigned_user_id,
        source=data.source,
    )
    deadline = await repo.create(deadline)

    domain_dl = ProceduralDeadline(
        id=deadline.id,
        matter_id=matter_id,
        title=data.title,
        due_at=data.due_at,
        status=DeadlineStatus.OPEN,
        priority=data.priority,
    )
    alert = evaluate_deadline_risk(domain_dl)
    if alert:
        alert_repo = AlertSQLRepository(session)
        await alert_repo.create(
            AlertModel(
                matter_id=alert.matter_id,
                alert_type=alert.alert_type,
                severity=alert.severity,
                title=alert.title,
                message=alert.message,
            )
        )

    audit_repo = AuditSQLRepository(session)
    await audit_repo.create(
        build_audit_event(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="deadline",
            resource_id=deadline.id,
            event_type=AuditEventType.CREATED,
            payload={"title": data.title, "due_at": data.due_at.isoformat()},
        )
    )
    return deadline


async def list_matter_deadlines(
    matter_id: UUID,
    *,
    session: AsyncSession,
) -> list[DeadlineModel]:
    repo = DeadlineSQLRepository(session)
    return await repo.list_by_matter(matter_id)


async def update_deadline(
    deadline_id: UUID,
    data: UpdateDeadlineRequest,
    *,
    session: AsyncSession,
) -> DeadlineModel:
    repo = DeadlineSQLRepository(session)
    dl = await repo.get_by_id(deadline_id)
    if not dl:
        raise NotFoundError("Deadline", deadline_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(dl, key, value)

    return await repo.update(dl)


async def complete_deadline(
    deadline_id: UUID,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> DeadlineModel:
    repo = DeadlineSQLRepository(session)
    dl = await repo.get_by_id(deadline_id)
    if not dl:
        raise NotFoundError("Deadline", deadline_id)

    dl.status = DeadlineStatus.COMPLETED
    dl.completed_at = datetime.now(UTC)
    dl = await repo.update(dl)

    audit_repo = AuditSQLRepository(session)
    await audit_repo.create(
        build_audit_event(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="deadline",
            resource_id=deadline_id,
            event_type=AuditEventType.DEADLINE_COMPLETED,
        )
    )
    return dl


async def get_upcoming_deadlines(
    *,
    tenant_id: UUID,
    session: AsyncSession,
    hours: int = 72,
    limit: int = 50,
) -> list[DeadlineModel]:
    repo = DeadlineSQLRepository(session)
    before = datetime.now(UTC) + timedelta(hours=hours)
    return await repo.list_upcoming(tenant_id, before, limit=limit)


async def get_overdue_deadlines(
    *,
    tenant_id: UUID,
    session: AsyncSession,
    limit: int = 50,
) -> list[DeadlineModel]:
    repo = DeadlineSQLRepository(session)
    return await repo.list_overdue(tenant_id, limit=limit)
