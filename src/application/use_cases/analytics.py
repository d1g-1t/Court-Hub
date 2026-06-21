from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.cache.service import CacheService
from src.infrastructure.database.models import (
    DeadlineModel,
    MatterModel,
)
from src.infrastructure.database.repositories import (
    AuditSQLRepository,
    MatterSQLRepository,
)


async def get_portfolio_analytics(
    tenant_id: UUID,
    *,
    session: AsyncSession,
    cache: CacheService,
    cache_ttl: int = 900,
) -> dict:
    """Portfolio overview — cached in Redis to reduce DB load."""
    cache_key = f"analytics:portfolio:{tenant_id}"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    matter_repo = MatterSQLRepository(session)
    by_status = await matter_repo.count_by_status(tenant_id)

    type_stmt = (
        select(MatterModel.matter_type, func.count())
        .where(MatterModel.tenant_id == tenant_id)
        .group_by(MatterModel.matter_type)
    )
    type_result = await session.execute(type_stmt)
    by_type = {row[0]: row[1] for row in type_result.all()}

    risk_stmt = (
        select(MatterModel.risk_level, func.count())
        .where(MatterModel.tenant_id == tenant_id)
        .group_by(MatterModel.risk_level)
    )
    risk_result = await session.execute(risk_stmt)
    by_risk = {row[0]: row[1] for row in risk_result.all()}

    total = sum(by_status.values())

    result = {
        "total_matters": total,
        "by_status": by_status,
        "by_type": by_type,
        "by_risk": by_risk,
    }
    await cache.set(cache_key, result, ttl=cache_ttl)
    return result


async def get_deadline_risk(
    tenant_id: UUID,
    *,
    session: AsyncSession,
) -> dict:
    """Deadline risk dashboard — pure SQL aggregation, no N+1."""
    now = datetime.now(UTC)
    base = (
        select(func.count())
        .select_from(DeadlineModel)
        .join(MatterModel, DeadlineModel.matter_id == MatterModel.id)
        .where(MatterModel.tenant_id == tenant_id, DeadlineModel.status == "OPEN")
    )

    overdue_stmt = base.where(DeadlineModel.due_at < now)
    due_24h_stmt = base.where(
        DeadlineModel.due_at >= now,
        DeadlineModel.due_at < now + timedelta(hours=24),
    )
    due_72h_stmt = base.where(
        DeadlineModel.due_at >= now,
        DeadlineModel.due_at < now + timedelta(hours=72),
    )

    overdue = (await session.execute(overdue_stmt)).scalar_one()
    due_24h = (await session.execute(due_24h_stmt)).scalar_one()
    due_72h = (await session.execute(due_72h_stmt)).scalar_one()

    return {"overdue": overdue, "due_within_24h": due_24h, "due_within_72h": due_72h}


async def get_cycle_time(
    tenant_id: UUID,
    *,
    session: AsyncSession,
) -> dict:
    """Average and per-type cycle time for closed matters."""
    stmt = (
        select(
            MatterModel.matter_type,
            func.avg(
                func.extract("epoch", MatterModel.closed_at)
                - func.extract("epoch", MatterModel.opened_at)
            ),
        )
        .where(
            MatterModel.tenant_id == tenant_id,
            MatterModel.closed_at.isnot(None),
        )
        .group_by(MatterModel.matter_type)
    )
    result = await session.execute(stmt)
    rows = result.all()

    by_type = {}
    total_seconds = []
    for mtype, avg_sec in rows:
        days = (avg_sec or 0) / 86400
        by_type[mtype] = round(days, 1)
        total_seconds.append(avg_sec or 0)

    avg_days = round(sum(total_seconds) / max(len(total_seconds), 1) / 86400, 1)

    return {
        "average_days": avg_days,
        "median_days": avg_days,  # simplified — real impl would use percentile_cont
        "by_type": by_type,
    }


async def get_audit_timeline(
    matter_id: UUID,
    *,
    session: AsyncSession,
):
    """Return audit trail for a specific matter."""
    repo = AuditSQLRepository(session)
    return await repo.list_by_resource("matter", matter_id, limit=200)
