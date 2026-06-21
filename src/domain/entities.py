from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from src.domain.value_objects import (
    AlertSeverity,
    AlertType,
    AuditEventType,
    BudgetEntryType,
    ClaimStatus,
    DeadlinePriority,
    DeadlineStatus,
    DefenseStatus,
    EvidenceType,
    HearingStatus,
    IssueSeverity,
    IssueStatus,
    MatterStatus,
    MatterType,
    NoteType,
    PrivilegeLevel,
    RiskLevel,
    RoleInCase,
)


@dataclass(slots=True, kw_only=True)
class Tenant:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    slug: str = ""
    is_active: bool = True
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class User:
    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = field(default_factory=uuid4)
    email: str = ""
    hashed_password: str = ""
    role: str = "viewer"
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class Matter:
    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = field(default_factory=uuid4)
    matter_number: str = ""
    title: str = ""
    matter_type: MatterType = MatterType.CIVIL
    court_system: str = ""
    court_name: str | None = None
    case_reference: str | None = None
    role_in_case: RoleInCase = RoleInCase.CLAIMANT
    status: MatterStatus = MatterStatus.OPEN
    risk_level: RiskLevel = RiskLevel.MEDIUM
    business_unit: str | None = None
    owner_user_id: UUID | None = None
    outside_counsel_required: bool = False
    estimated_exposure: Decimal | None = None
    currency: str | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class MatterParty:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    party_role: str = ""
    legal_name: str = ""
    inn: str | None = None
    ogrn: str | None = None
    representative_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, kw_only=True)
class Hearing:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    hearing_type: str = ""
    scheduled_at: datetime | None = None
    courtroom: str | None = None
    judge_name: str | None = None
    status: HearingStatus = HearingStatus.SCHEDULED
    outcome_summary: str | None = None
    source_system: str | None = None
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class ProceduralDeadline:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    deadline_type: str = ""
    title: str = ""
    due_at: datetime | None = None
    status: DeadlineStatus = DeadlineStatus.OPEN
    source: str = ""
    priority: DeadlinePriority = DeadlinePriority.NORMAL
    assigned_user_id: UUID | None = None
    escalation_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, kw_only=True)
class EvidenceItem:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    file_name: str = ""
    mime_type: str = ""
    storage_path: str = ""
    checksum: str = ""
    evidence_type: EvidenceType = EvidenceType.DOCUMENT
    privilege_level: PrivilegeLevel = PrivilegeLevel.STANDARD
    source_description: str | None = None
    admissibility_note: str | None = None
    uploaded_by: UUID | None = None
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class Issue:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    severity: IssueSeverity = IssueSeverity.MEDIUM
    status: IssueStatus = IssueStatus.OPEN
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class Claim:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    title: str = ""
    amount: Decimal | None = None
    currency: str | None = None
    status: ClaimStatus = ClaimStatus.OPEN
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, kw_only=True)
class Defense:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    title: str = ""
    status: DefenseStatus = DefenseStatus.ACTIVE
    strategy_note: str | None = None


@dataclass(slots=True, kw_only=True)
class ChronologyEvent:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    event_at: datetime | None = None
    title: str = ""
    description: str = ""
    source_type: str = ""
    source_id: UUID | None = None
    ai_generated: bool = False
    confidence: float | None = None
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class OutsideCounselAssignment:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    firm_name: str = ""
    lead_lawyer: str | None = None
    scoped_access: list[str] = field(default_factory=list)
    engagement_terms: dict[str, Any] = field(default_factory=dict)
    started_at: datetime | None = None
    ended_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class BudgetEntry:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    entry_type: BudgetEntryType = BudgetEntryType.EXPENSE
    amount: Decimal = Decimal("0")
    currency: str = "RUB"
    vendor_name: str | None = None
    description: str | None = None
    incurred_at: datetime | None = None
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class ReviewNote:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    author_user_id: UUID = field(default_factory=uuid4)
    note_type: NoteType = NoteType.GENERAL
    body: str = ""
    related_deadline_id: UUID | None = None
    related_hearing_id: UUID | None = None
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class Alert:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    alert_type: AlertType = AlertType.DEADLINE_WARNING
    severity: AlertSeverity = AlertSeverity.WARNING
    title: str = ""
    message: str = ""
    acknowledged: bool = False
    acknowledged_by: UUID | None = None
    acknowledged_at: datetime | None = None
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class AIAnalysisRun:
    id: UUID = field(default_factory=uuid4)
    matter_id: UUID = field(default_factory=uuid4)
    pipeline_type: str = ""
    model_name: str = ""
    prompt_hash: str = ""
    prompt_version: str = ""
    input_snapshot: dict[str, Any] = field(default_factory=dict)
    output_snapshot: dict[str, Any] = field(default_factory=dict)
    status: str = ""
    latency_ms: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    trace_id: str | None = None
    created_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class AuditEvent:
    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = field(default_factory=uuid4)
    actor_user_id: UUID | None = None
    resource_type: str = ""
    resource_id: UUID = field(default_factory=uuid4)
    event_type: AuditEventType = AuditEventType.CREATED
    trace_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
