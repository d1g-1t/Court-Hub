from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    type_annotation_map = {
        dict[str, Any]: JSONB,
    }


def _uuid_pk() -> Mapped[str]:
    return mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


def _utc_now() -> Mapped[datetime]:
    return mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )


class TenantModel(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = _uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = _utc_now()

    users: Mapped[list["UserModel"]] = relationship(back_populates="tenant", lazy="selectin")
    matters: Mapped[list["MatterModel"]] = relationship(back_populates="tenant", lazy="noload")


class UserModel(Base):
    __tablename__ = "api_users"

    id: Mapped[str] = _uuid_pk()
    tenant_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="viewer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = _utc_now()
    updated_at: Mapped[datetime] = _utc_now()

    tenant: Mapped["TenantModel"] = relationship(back_populates="users", lazy="joined")


class MatterModel(Base):
    __tablename__ = "matters"
    __table_args__ = (
        Index("idx_matters_status", "tenant_id", "status"),
        Index("idx_matters_owner", "owner_user_id", "status"),
    )

    id: Mapped[str] = _uuid_pk()
    tenant_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    matter_number: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    matter_type: Mapped[str] = mapped_column(String(64), nullable=False)
    court_system: Mapped[str] = mapped_column(String(64), nullable=False)
    court_name: Mapped[str | None] = mapped_column(String(255))
    case_reference: Mapped[str | None] = mapped_column(String(128))
    role_in_case: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="MEDIUM")
    business_unit: Mapped[str | None] = mapped_column(String(128))
    owner_user_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("api_users.id")
    )
    outside_counsel_required: Mapped[bool] = mapped_column(Boolean, default=False)
    estimated_exposure: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    currency: Mapped[str | None] = mapped_column(String(3))
    opened_at: Mapped[datetime] = _utc_now()
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, server_default="{}"
    )
    created_at: Mapped[datetime] = _utc_now()
    updated_at: Mapped[datetime] = _utc_now()

    tenant: Mapped["TenantModel"] = relationship(back_populates="matters", lazy="noload")
    parties: Mapped[list["MatterPartyModel"]] = relationship(
        back_populates="matter", lazy="selectin", cascade="all, delete-orphan"
    )
    hearings: Mapped[list["HearingModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    deadlines: Mapped[list["DeadlineModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    evidence_items: Mapped[list["EvidenceModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    issues: Mapped[list["IssueModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    claims: Mapped[list["ClaimModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    defenses: Mapped[list["DefenseModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    chronology_events: Mapped[list["ChronologyEventModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    counsel_assignments: Mapped[list["OutsideCounselModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    budget_entries: Mapped[list["BudgetEntryModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["AlertModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    review_notes: Mapped[list["ReviewNoteModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )
    ai_runs: Mapped[list["AIAnalysisRunModel"]] = relationship(
        back_populates="matter", lazy="noload", cascade="all, delete-orphan"
    )


class MatterPartyModel(Base):
    __tablename__ = "matter_parties"

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    party_role: Mapped[str] = mapped_column(String(32), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str | None] = mapped_column(String(12))
    ogrn: Mapped[str | None] = mapped_column(String(15))
    representative_name: Mapped[str | None] = mapped_column(String(255))
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, server_default="{}"
    )

    matter: Mapped["MatterModel"] = relationship(back_populates="parties", lazy="noload")


class HearingModel(Base):
    __tablename__ = "hearings"
    __table_args__ = (Index("idx_hearings_scheduled", "scheduled_at", "status"),)

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    hearing_type: Mapped[str] = mapped_column(String(64), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    courtroom: Mapped[str | None] = mapped_column(String(128))
    judge_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SCHEDULED")
    outcome_summary: Mapped[str | None] = mapped_column(Text)
    source_system: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = _utc_now()

    matter: Mapped["MatterModel"] = relationship(back_populates="hearings", lazy="noload")


class DeadlineModel(Base):
    __tablename__ = "procedural_deadlines"
    __table_args__ = (Index("idx_deadlines_due", "due_at", "status"),)

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    deadline_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    priority: Mapped[str] = mapped_column(String(32), nullable=False, default="NORMAL")
    assigned_user_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("api_users.id")
    )
    escalation_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, server_default="{}"
    )

    matter: Mapped["MatterModel"] = relationship(back_populates="deadlines", lazy="noload")


class EvidenceModel(Base):
    __tablename__ = "evidence_items"

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    privilege_level: Mapped[str] = mapped_column(String(32), nullable=False, default="STANDARD")
    source_description: Mapped[str | None] = mapped_column(Text)
    admissibility_note: Mapped[str | None] = mapped_column(Text)
    uploaded_by: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("api_users.id"), nullable=False
    )
    created_at: Mapped[datetime] = _utc_now()

    matter: Mapped["MatterModel"] = relationship(back_populates="evidence_items", lazy="noload")


class IssueModel(Base):
    __tablename__ = "issues"

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="MEDIUM")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    created_at: Mapped[datetime] = _utc_now()

    matter: Mapped["MatterModel"] = relationship(back_populates="issues", lazy="noload")


class ClaimModel(Base):
    __tablename__ = "claims"

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    currency: Mapped[str | None] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, server_default="{}"
    )

    matter: Mapped["MatterModel"] = relationship(back_populates="claims", lazy="noload")


class DefenseModel(Base):
    __tablename__ = "defenses"

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    strategy_note: Mapped[str | None] = mapped_column(Text)

    matter: Mapped["MatterModel"] = relationship(back_populates="defenses", lazy="noload")


class ChronologyEventModel(Base):
    __tablename__ = "chronology_events"

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    event_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True))
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    created_at: Mapped[datetime] = _utc_now()

    matter: Mapped["MatterModel"] = relationship(
        back_populates="chronology_events", lazy="noload"
    )


class OutsideCounselModel(Base):
    __tablename__ = "outside_counsel_assignments"

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    firm_name: Mapped[str] = mapped_column(String(255), nullable=False)
    lead_lawyer: Mapped[str | None] = mapped_column(String(255))
    scoped_access: Mapped[dict[str, Any]] = mapped_column(JSONB, default=list, server_default="[]")
    engagement_terms: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )
    started_at: Mapped[datetime] = _utc_now()
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    matter: Mapped["MatterModel"] = relationship(
        back_populates="counsel_assignments", lazy="noload"
    )


class BudgetEntryModel(Base):
    __tablename__ = "budget_entries"

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    entry_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    vendor_name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    incurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = _utc_now()

    matter: Mapped["MatterModel"] = relationship(back_populates="budget_entries", lazy="noload")


class ReviewNoteModel(Base):
    __tablename__ = "review_notes"

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    author_user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("api_users.id"), nullable=False
    )
    note_type: Mapped[str] = mapped_column(String(32), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    related_deadline_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("procedural_deadlines.id")
    )
    related_hearing_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("hearings.id")
    )
    created_at: Mapped[datetime] = _utc_now()

    matter: Mapped["MatterModel"] = relationship(back_populates="review_notes", lazy="noload")


class AlertModel(Base):
    __tablename__ = "alerts"
    __table_args__ = (Index("idx_alerts_ack", "acknowledged", "created_at"),)

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_by: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("api_users.id")
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _utc_now()

    matter: Mapped["MatterModel"] = relationship(back_populates="alerts", lazy="noload")


class AIAnalysisRunModel(Base):
    __tablename__ = "ai_analysis_runs"
    __table_args__ = (Index("idx_ai_runs_matter", "matter_id", "created_at"),)

    id: Mapped[str] = _uuid_pk()
    matter_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    pipeline_type: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(32), nullable=False)
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    output_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    trace_id: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = _utc_now()

    matter: Mapped["MatterModel"] = relationship(back_populates="ai_runs", lazy="noload")


class AuditEventModel(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        Index("idx_audit_resource", "resource_type", "resource_id", "created_at"),
    )

    id: Mapped[str] = _uuid_pk()
    tenant_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    actor_user_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("api_users.id")
    )
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(128))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = _utc_now()
