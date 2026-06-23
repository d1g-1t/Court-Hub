from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.infrastructure.database.models import (
    AIAnalysisRunModel,
    AlertModel,
    AuditEventModel,
    BudgetEntryModel,
    ChronologyEventModel,
    ClaimModel,
    DeadlineModel,
    DefenseModel,
    EvidenceModel,
    HearingModel,
    IssueModel,
    MatterModel,
    MatterPartyModel,
    OutsideCounselModel,
    ReviewNoteModel,
    UserModel,
)


class _BaseSQLRepo[T]:

    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> T | None:
        return await self.session.get(self.model, entity_id)

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, obj: T) -> T:
        merged = await self.session.merge(obj)
        await self.session.flush()
        return merged

    async def delete(self, entity_id: UUID) -> None:
        obj = await self.get_by_id(entity_id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()

    async def list_all(
        self,
        *,
        tenant_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[T]:
        stmt = select(self.model).limit(limit).offset(offset)
        if tenant_id and hasattr(self.model, "tenant_id"):
            stmt = stmt.where(self.model.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class UserSQLRepository(_BaseSQLRepo[UserModel]):
    model = UserModel

    async def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class MatterSQLRepository(_BaseSQLRepo[MatterModel]):
    model = MatterModel

    async def get_by_id(self, entity_id: UUID) -> MatterModel | None:
        stmt = (
            select(MatterModel)
            .options(selectinload(MatterModel.parties))
            .where(MatterModel.id == entity_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(self, tenant_id: UUID, matter_number: str) -> MatterModel | None:
        stmt = select(MatterModel).where(
            MatterModel.tenant_id == tenant_id,
            MatterModel.matter_number == matter_number,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_status(
        self,
        tenant_id: UUID,
        status: str,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MatterModel]:
        stmt = (
            select(MatterModel)
            .options(selectinload(MatterModel.parties))
            .where(MatterModel.tenant_id == tenant_id, MatterModel.status == status)
            .order_by(MatterModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all(
        self,
        *,
        tenant_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MatterModel]:
        stmt = (
            select(MatterModel)
            .options(selectinload(MatterModel.parties))
            .order_by(MatterModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if tenant_id:
            stmt = stmt.where(MatterModel.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_status(self, tenant_id: UUID) -> dict[str, int]:
        stmt = (
            select(MatterModel.status, func.count())
            .where(MatterModel.tenant_id == tenant_id)
            .group_by(MatterModel.status)
        )
        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}


class DeadlineSQLRepository(_BaseSQLRepo[DeadlineModel]):
    model = DeadlineModel

    async def list_by_matter(self, matter_id: UUID) -> list[DeadlineModel]:
        stmt = (
            select(DeadlineModel)
            .where(DeadlineModel.matter_id == matter_id)
            .order_by(DeadlineModel.due_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_upcoming(
        self, tenant_id: UUID, before: datetime, *, limit: int = 50
    ) -> list[DeadlineModel]:
        now = datetime.now(UTC)
        stmt = (
            select(DeadlineModel)
            .join(MatterModel, DeadlineModel.matter_id == MatterModel.id)
            .where(
                MatterModel.tenant_id == tenant_id,
                DeadlineModel.status == "OPEN",
                DeadlineModel.due_at >= now,
                DeadlineModel.due_at <= before,
            )
            .order_by(DeadlineModel.due_at)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_overdue(self, tenant_id: UUID, *, limit: int = 50) -> list[DeadlineModel]:
        now = datetime.now(UTC)
        stmt = (
            select(DeadlineModel)
            .join(MatterModel, DeadlineModel.matter_id == MatterModel.id)
            .where(
                MatterModel.tenant_id == tenant_id,
                DeadlineModel.status == "OPEN",
                DeadlineModel.due_at < now,
            )
            .order_by(DeadlineModel.due_at)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class HearingSQLRepository(_BaseSQLRepo[HearingModel]):
    model = HearingModel

    async def list_by_matter(self, matter_id: UUID) -> list[HearingModel]:
        stmt = (
            select(HearingModel)
            .where(HearingModel.matter_id == matter_id)
            .order_by(HearingModel.scheduled_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class EvidenceSQLRepository(_BaseSQLRepo[EvidenceModel]):
    model = EvidenceModel

    async def list_by_matter(self, matter_id: UUID) -> list[EvidenceModel]:
        stmt = (
            select(EvidenceModel)
            .where(EvidenceModel.matter_id == matter_id)
            .order_by(EvidenceModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class IssueSQLRepository(_BaseSQLRepo[IssueModel]):
    model = IssueModel

    async def list_by_matter(self, matter_id: UUID) -> list[IssueModel]:
        stmt = select(IssueModel).where(IssueModel.matter_id == matter_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ClaimSQLRepository(_BaseSQLRepo[ClaimModel]):
    model = ClaimModel

    async def list_by_matter(self, matter_id: UUID) -> list[ClaimModel]:
        stmt = select(ClaimModel).where(ClaimModel.matter_id == matter_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class DefenseSQLRepository(_BaseSQLRepo[DefenseModel]):
    model = DefenseModel

    async def list_by_matter(self, matter_id: UUID) -> list[DefenseModel]:
        stmt = select(DefenseModel).where(DefenseModel.matter_id == matter_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ChronologySQLRepository(_BaseSQLRepo[ChronologyEventModel]):
    model = ChronologyEventModel

    async def list_by_matter(self, matter_id: UUID) -> list[ChronologyEventModel]:
        stmt = (
            select(ChronologyEventModel)
            .where(ChronologyEventModel.matter_id == matter_id)
            .order_by(ChronologyEventModel.event_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class OutsideCounselSQLRepository(_BaseSQLRepo[OutsideCounselModel]):
    model = OutsideCounselModel

    async def list_by_matter(self, matter_id: UUID) -> list[OutsideCounselModel]:
        stmt = (
            select(OutsideCounselModel)
            .where(OutsideCounselModel.matter_id == matter_id)
            .order_by(OutsideCounselModel.started_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class BudgetSQLRepository(_BaseSQLRepo[BudgetEntryModel]):
    model = BudgetEntryModel

    async def list_by_matter(self, matter_id: UUID) -> list[BudgetEntryModel]:
        stmt = (
            select(BudgetEntryModel)
            .where(BudgetEntryModel.matter_id == matter_id)
            .order_by(BudgetEntryModel.incurred_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def total_spend_by_matter(self, matter_id: UUID) -> float:
        stmt = select(func.coalesce(func.sum(BudgetEntryModel.amount), 0)).where(
            BudgetEntryModel.matter_id == matter_id
        )
        result = await self.session.execute(stmt)
        return float(result.scalar_one())


class AlertSQLRepository(_BaseSQLRepo[AlertModel]):
    model = AlertModel

    async def list_unacknowledged(
        self, tenant_id: UUID, *, limit: int = 50
    ) -> list[AlertModel]:
        stmt = (
            select(AlertModel)
            .join(MatterModel, AlertModel.matter_id == MatterModel.id)
            .where(MatterModel.tenant_id == tenant_id, AlertModel.acknowledged.is_(False))
            .order_by(AlertModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class AuditSQLRepository(_BaseSQLRepo[AuditEventModel]):
    model = AuditEventModel

    async def list_by_resource(
        self, resource_type: str, resource_id: UUID, *, limit: int = 100
    ) -> list[AuditEventModel]:
        stmt = (
            select(AuditEventModel)
            .where(
                AuditEventModel.resource_type == resource_type,
                AuditEventModel.resource_id == resource_id,
            )
            .order_by(AuditEventModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class AIRunSQLRepository(_BaseSQLRepo[AIAnalysisRunModel]):
    model = AIAnalysisRunModel

    async def list_by_matter(self, matter_id: UUID) -> list[AIAnalysisRunModel]:
        stmt = (
            select(AIAnalysisRunModel)
            .where(AIAnalysisRunModel.matter_id == matter_id)
            .order_by(AIAnalysisRunModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ReviewNoteSQLRepository(_BaseSQLRepo[ReviewNoteModel]):
    model = ReviewNoteModel

    async def list_by_matter(self, matter_id: UUID) -> list[ReviewNoteModel]:
        stmt = (
            select(ReviewNoteModel)
            .where(ReviewNoteModel.matter_id == matter_id)
            .order_by(ReviewNoteModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class PartySQLRepository(_BaseSQLRepo[MatterPartyModel]):
    model = MatterPartyModel

    async def list_by_matter(self, matter_id: UUID) -> list[MatterPartyModel]:
        stmt = select(MatterPartyModel).where(MatterPartyModel.matter_id == matter_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
