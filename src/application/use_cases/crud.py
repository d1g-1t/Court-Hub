from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto import (
    AssignOutsideCounselRequest,
    CreateBudgetEntryRequest,
    CreateClaimRequest,
    CreateDefenseRequest,
    CreateIssueRequest,
    EvidenceUploadMeta,
    UpdateIssueRequest,
)
from src.domain.exceptions import NotFoundError
from src.domain.services import build_audit_event
from src.domain.value_objects import AuditEventType
from src.infrastructure.database.models import (
    AlertModel,
    BudgetEntryModel,
    ClaimModel,
    DefenseModel,
    EvidenceModel,
    IssueModel,
    MatterModel,
    OutsideCounselModel,
)
from src.infrastructure.database.repositories import (
    AlertSQLRepository,
    AuditSQLRepository,
    BudgetSQLRepository,
    ClaimSQLRepository,
    DefenseSQLRepository,
    EvidenceSQLRepository,
    IssueSQLRepository,
    MatterSQLRepository,
    OutsideCounselSQLRepository,
)


async def upload_evidence(
    matter_id: UUID,
    file_name: str,
    mime_type: str,
    file_bytes: bytes,
    meta: EvidenceUploadMeta,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> EvidenceModel:
    matter_repo = MatterSQLRepository(session)
    if not await matter_repo.get_by_id(matter_id):
        raise NotFoundError("Matter", matter_id)

    checksum = hashlib.sha256(file_bytes).hexdigest()
    storage_path = f"evidence/{matter_id}/{checksum}/{file_name}"

    repo = EvidenceSQLRepository(session)
    evidence = EvidenceModel(
        matter_id=matter_id,
        file_name=file_name,
        mime_type=mime_type,
        storage_path=storage_path,
        checksum=checksum,
        evidence_type=meta.evidence_type,
        privilege_level=meta.privilege_level,
        source_description=meta.source_description,
        admissibility_note=meta.admissibility_note,
        uploaded_by=user_id,
    )
    evidence = await repo.create(evidence)

    audit_repo = AuditSQLRepository(session)
    await audit_repo.create(
        build_audit_event(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="evidence",
            resource_id=evidence.id,
            event_type=AuditEventType.EVIDENCE_UPLOADED,
            payload={"file_name": file_name, "evidence_type": meta.evidence_type},
        )
    )
    return evidence


async def list_matter_evidence(
    matter_id: UUID,
    *,
    session: AsyncSession,
) -> list[EvidenceModel]:
    repo = EvidenceSQLRepository(session)
    return await repo.list_by_matter(matter_id)


async def get_evidence(
    evidence_id: UUID,
    *,
    session: AsyncSession,
) -> EvidenceModel:
    repo = EvidenceSQLRepository(session)
    ev = await repo.get_by_id(evidence_id)
    if not ev:
        raise NotFoundError("Evidence", evidence_id)
    return ev


async def create_issue(
    matter_id: UUID,
    data: CreateIssueRequest,
    *,
    session: AsyncSession,
) -> IssueModel:
    matter_repo = MatterSQLRepository(session)
    if not await matter_repo.get_by_id(matter_id):
        raise NotFoundError("Matter", matter_id)

    repo = IssueSQLRepository(session)
    issue = IssueModel(
        matter_id=matter_id,
        title=data.title,
        description=data.description,
        severity=data.severity,
    )
    return await repo.create(issue)


async def list_matter_issues(
    matter_id: UUID,
    *,
    session: AsyncSession,
) -> list[IssueModel]:
    repo = IssueSQLRepository(session)
    return await repo.list_by_matter(matter_id)


async def update_issue(
    issue_id: UUID,
    data: UpdateIssueRequest,
    *,
    session: AsyncSession,
) -> IssueModel:
    repo = IssueSQLRepository(session)
    issue = await repo.get_by_id(issue_id)
    if not issue:
        raise NotFoundError("Issue", issue_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(issue, key, value)
    return await repo.update(issue)


async def create_claim(
    matter_id: UUID,
    data: CreateClaimRequest,
    *,
    session: AsyncSession,
) -> ClaimModel:
    matter_repo = MatterSQLRepository(session)
    if not await matter_repo.get_by_id(matter_id):
        raise NotFoundError("Matter", matter_id)

    repo = ClaimSQLRepository(session)
    claim = ClaimModel(
        matter_id=matter_id,
        title=data.title,
        amount=data.amount,
        currency=data.currency,
    )
    return await repo.create(claim)


async def list_matter_claims(
    matter_id: UUID,
    *,
    session: AsyncSession,
) -> list[ClaimModel]:
    repo = ClaimSQLRepository(session)
    return await repo.list_by_matter(matter_id)


async def create_defense(
    matter_id: UUID,
    data: CreateDefenseRequest,
    *,
    session: AsyncSession,
) -> DefenseModel:
    matter_repo = MatterSQLRepository(session)
    if not await matter_repo.get_by_id(matter_id):
        raise NotFoundError("Matter", matter_id)

    repo = DefenseSQLRepository(session)
    defense = DefenseModel(
        matter_id=matter_id,
        title=data.title,
        strategy_note=data.strategy_note,
    )
    return await repo.create(defense)


async def list_matter_defenses(
    matter_id: UUID,
    *,
    session: AsyncSession,
) -> list[DefenseModel]:
    repo = DefenseSQLRepository(session)
    return await repo.list_by_matter(matter_id)


async def assign_counsel(
    matter_id: UUID,
    data: AssignOutsideCounselRequest,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> OutsideCounselModel:
    matter_repo = MatterSQLRepository(session)
    matter = await matter_repo.get_by_id(matter_id)
    if not matter:
        raise NotFoundError("Matter", matter_id)

    repo = OutsideCounselSQLRepository(session)
    assignment = OutsideCounselModel(
        matter_id=matter_id,
        firm_name=data.firm_name,
        lead_lawyer=data.lead_lawyer,
        scoped_access=data.scoped_access,
    )
    assignment = await repo.create(assignment)

    matter.outside_counsel_required = True
    await matter_repo.update(matter)

    audit_repo = AuditSQLRepository(session)
    await audit_repo.create(
        build_audit_event(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="counsel_assignment",
            resource_id=assignment.id,
            event_type=AuditEventType.COUNSEL_ASSIGNED,
            payload={"firm_name": data.firm_name},
        )
    )
    return assignment


async def list_matter_counsel(
    matter_id: UUID,
    *,
    session: AsyncSession,
) -> list[OutsideCounselModel]:
    repo = OutsideCounselSQLRepository(session)
    return await repo.list_by_matter(matter_id)


async def end_counsel_assignment(
    assignment_id: UUID,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> OutsideCounselModel:
    repo = OutsideCounselSQLRepository(session)
    assignment = await repo.get_by_id(assignment_id)
    if not assignment:
        raise NotFoundError("CounselAssignment", assignment_id)

    assignment.ended_at = datetime.now(UTC)
    assignment = await repo.update(assignment)

    audit_repo = AuditSQLRepository(session)
    await audit_repo.create(
        build_audit_event(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="counsel_assignment",
            resource_id=assignment_id,
            event_type=AuditEventType.COUNSEL_ENDED,
        )
    )
    return assignment


async def create_budget_entry(
    matter_id: UUID,
    data: CreateBudgetEntryRequest,
    *,
    session: AsyncSession,
) -> BudgetEntryModel:
    matter_repo = MatterSQLRepository(session)
    if not await matter_repo.get_by_id(matter_id):
        raise NotFoundError("Matter", matter_id)

    repo = BudgetSQLRepository(session)
    entry = BudgetEntryModel(
        matter_id=matter_id,
        entry_type=data.entry_type,
        amount=data.amount,
        currency=data.currency,
        vendor_name=data.vendor_name,
        description=data.description,
        incurred_at=data.incurred_at,
    )
    return await repo.create(entry)


async def list_matter_budget(
    matter_id: UUID,
    *,
    session: AsyncSession,
) -> list[BudgetEntryModel]:
    repo = BudgetSQLRepository(session)
    return await repo.list_by_matter(matter_id)


async def get_spend_analytics(
    tenant_id: UUID,
    *,
    session: AsyncSession,
) -> dict:
    total_stmt = (
        select(func.coalesce(func.sum(BudgetEntryModel.amount), 0))
        .join(MatterModel, BudgetEntryModel.matter_id == MatterModel.id)
        .where(MatterModel.tenant_id == tenant_id)
    )
    total_result = await session.execute(total_stmt)
    total = total_result.scalar_one()

    vendor_stmt = (
        select(BudgetEntryModel.vendor_name, func.sum(BudgetEntryModel.amount))
        .join(MatterModel, BudgetEntryModel.matter_id == MatterModel.id)
        .where(MatterModel.tenant_id == tenant_id, BudgetEntryModel.vendor_name.isnot(None))
        .group_by(BudgetEntryModel.vendor_name)
    )
    vendor_result = await session.execute(vendor_stmt)
    by_vendor = {row[0]: Decimal(str(row[1])) for row in vendor_result.all()}

    type_stmt = (
        select(BudgetEntryModel.entry_type, func.sum(BudgetEntryModel.amount))
        .join(MatterModel, BudgetEntryModel.matter_id == MatterModel.id)
        .where(MatterModel.tenant_id == tenant_id)
        .group_by(BudgetEntryModel.entry_type)
    )
    type_result = await session.execute(type_stmt)
    by_entry_type = {row[0]: Decimal(str(row[1])) for row in type_result.all()}

    return {
        "total_spend": Decimal(str(total)),
        "by_vendor": by_vendor,
        "by_entry_type": by_entry_type,
    }


async def list_alerts(
    tenant_id: UUID,
    *,
    session: AsyncSession,
    limit: int = 50,
) -> list[AlertModel]:
    repo = AlertSQLRepository(session)
    return await repo.list_unacknowledged(tenant_id, limit=limit)


async def acknowledge_alert(
    alert_id: UUID,
    *,
    tenant_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> AlertModel:
    repo = AlertSQLRepository(session)
    alert = await repo.get_by_id(alert_id)
    if not alert:
        raise NotFoundError("Alert", alert_id)

    alert.acknowledged = True
    alert.acknowledged_by = user_id
    alert.acknowledged_at = datetime.now(UTC)
    alert = await repo.update(alert)

    audit_repo = AuditSQLRepository(session)
    await audit_repo.create(
        build_audit_event(
            tenant_id=tenant_id,
            actor_user_id=user_id,
            resource_type="alert",
            resource_id=alert_id,
            event_type=AuditEventType.ALERT_ACKNOWLEDGED,
        )
    )
    return alert
