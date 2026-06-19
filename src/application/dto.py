from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime


class CreateMatterRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    matter_type: Literal[
        "CIVIL", "COMMERCIAL", "ADMINISTRATIVE", "BANKRUPTCY",
        "TAX", "LABOR", "IP", "CRIMINAL", "OTHER",
    ]
    court_system: Literal[
        "ARBITRAZH", "GENERAL_JURISDICTION", "SUPREME_COURT",
        "CONSTITUTIONAL_COURT", "CASSATION", "APPEAL", "OTHER",
    ]
    court_name: str | None = None
    case_reference: str | None = None
    role_in_case: Literal["CLAIMANT", "RESPONDENT", "THIRD_PARTY"]
    business_unit: str | None = None
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
    estimated_exposure: Decimal | None = None
    currency: str | None = None


class UpdateMatterRequest(BaseModel):
    title: str | None = None
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] | None = None
    business_unit: str | None = None
    court_name: str | None = None
    case_reference: str | None = None
    estimated_exposure: Decimal | None = None
    currency: str | None = None
    status: str | None = None


class MatterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    matter_number: str
    title: str
    matter_type: str
    court_system: str
    court_name: str | None
    case_reference: str | None
    role_in_case: str
    status: str
    risk_level: str
    business_unit: str | None
    owner_user_id: UUID | None
    outside_counsel_required: bool
    estimated_exposure: Decimal | None
    currency: str | None
    opened_at: datetime
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ImportFromCourtRequest(BaseModel):
    case_reference: str
    court_system: Literal["ARBITRAZH", "GENERAL_JURISDICTION"]


class CreatePartyRequest(BaseModel):
    party_role: str
    legal_name: str = Field(min_length=1, max_length=255)
    inn: str | None = None
    ogrn: str | None = None
    representative_name: str | None = None


class UpdatePartyRequest(BaseModel):
    party_role: str | None = None
    legal_name: str | None = None
    inn: str | None = None
    ogrn: str | None = None
    representative_name: str | None = None


class PartyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    party_role: str
    legal_name: str
    inn: str | None
    ogrn: str | None
    representative_name: str | None


class CreateHearingRequest(BaseModel):
    hearing_type: str
    scheduled_at: datetime
    courtroom: str | None = None
    judge_name: str | None = None


class UpdateHearingRequest(BaseModel):
    scheduled_at: datetime | None = None
    courtroom: str | None = None
    judge_name: str | None = None
    status: str | None = None


class HearingOutcomeRequest(BaseModel):
    outcome_summary: str


class HearingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    hearing_type: str
    scheduled_at: datetime
    courtroom: str | None
    judge_name: str | None
    status: str
    outcome_summary: str | None
    source_system: str | None
    created_at: datetime


class CreateDeadlineRequest(BaseModel):
    deadline_type: str
    title: str = Field(min_length=1, max_length=255)
    due_at: datetime
    priority: Literal["LOW", "NORMAL", "HIGH", "URGENT"] = "NORMAL"
    assigned_user_id: UUID | None = None
    source: str


class UpdateDeadlineRequest(BaseModel):
    title: str | None = None
    due_at: datetime | None = None
    priority: Literal["LOW", "NORMAL", "HIGH", "URGENT"] | None = None
    assigned_user_id: UUID | None = None


class DeadlineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    deadline_type: str
    title: str
    due_at: datetime
    status: str
    source: str
    priority: str
    assigned_user_id: UUID | None
    escalation_at: datetime | None
    completed_at: datetime | None


class EvidenceUploadMeta(BaseModel):
    evidence_type: Literal[
        "DOCUMENT", "WITNESS_STATEMENT", "EXPERT_REPORT",
        "CORRESPONDENCE", "FINANCIAL_RECORD", "PHOTO_VIDEO",
        "ELECTRONIC", "OTHER",
    ] = "DOCUMENT"
    privilege_level: Literal[
        "STANDARD", "ATTORNEY_CLIENT", "WORK_PRODUCT", "CONFIDENTIAL"
    ] = "STANDARD"
    source_description: str | None = None
    admissibility_note: str | None = None


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    file_name: str
    mime_type: str
    storage_path: str
    checksum: str
    evidence_type: str
    privilege_level: str
    source_description: str | None
    admissibility_note: str | None
    uploaded_by: UUID
    created_at: datetime


class CreateIssueRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"


class UpdateIssueRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime


class CreateClaimRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    amount: Decimal | None = None
    currency: str | None = None


class ClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    title: str
    amount: Decimal | None
    currency: str | None
    status: str


class CreateDefenseRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    strategy_note: str | None = None


class DefenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    title: str
    status: str
    strategy_note: str | None


class GenerateChronologyRequest(BaseModel):
    include_evidence: bool = True
    include_notes: bool = True
    min_confidence: float = 0.60


class ChronologyEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    event_at: datetime
    title: str
    description: str
    source_type: str
    source_id: UUID | None
    ai_generated: bool
    confidence: float | None
    created_at: datetime


class AIRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    pipeline_type: str
    model_name: str
    prompt_version: str
    status: str
    output_snapshot: dict[str, Any]
    latency_ms: int | None
    created_at: datetime


class AssignOutsideCounselRequest(BaseModel):
    firm_name: str = Field(min_length=1, max_length=255)
    lead_lawyer: str | None = None
    scoped_access: list[str] = Field(default_factory=list)


class OutsideCounselResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    firm_name: str
    lead_lawyer: str | None
    scoped_access: Any
    engagement_terms: Any
    started_at: datetime
    ended_at: datetime | None


class CreateBudgetEntryRequest(BaseModel):
    entry_type: Literal["BUDGET", "INVOICE", "EXPENSE", "SETTLEMENT"]
    amount: Decimal
    currency: str = "RUB"
    vendor_name: str | None = None
    description: str | None = None
    incurred_at: datetime


class BudgetEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    entry_type: str
    amount: Decimal
    currency: str
    vendor_name: str | None
    description: str | None
    incurred_at: datetime
    created_at: datetime


class SpendAnalyticsResponse(BaseModel):
    total_spend: Decimal
    by_vendor: dict[str, Decimal]
    by_entry_type: dict[str, Decimal]


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    alert_type: str
    severity: str
    title: str
    message: str
    acknowledged: bool
    acknowledged_by: UUID | None
    acknowledged_at: datetime | None
    created_at: datetime


class PortfolioAnalyticsResponse(BaseModel):
    total_matters: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    by_risk: dict[str, int]


class DeadlineRiskResponse(BaseModel):
    overdue: int
    due_within_24h: int
    due_within_72h: int


class CycleTimeResponse(BaseModel):
    average_days: float
    median_days: float
    by_type: dict[str, float]


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    actor_user_id: UUID | None
    resource_type: str
    resource_id: UUID
    event_type: str
    trace_id: str | None
    payload: dict[str, Any]
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"


class ReadinessResponse(BaseModel):
    status: str
    postgres: bool
    redis: bool


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    limit: int
    offset: int
