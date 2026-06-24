"""001 – initial schema

Revision ID: 001_initial
Revises: None
Create Date: 2025-01-01 00:00:00
"""
from __future__ import annotations

from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UUID = postgresql.UUID(as_uuid=True)
_JSONB = postgresql.JSONB()
_TS = sa.DateTime(timezone=True)


def upgrade() -> None:
    # ── Tenants ────────────────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(128), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
    )

    # ── Users ──────────────────────────────────────────────
    op.create_table(
        "api_users",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column("tenant_id", _UUID, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(64), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
        sa.Column("updated_at", _TS, server_default=sa.func.now()),
    )

    # ── Matters ────────────────────────────────────────────
    op.create_table(
        "matters",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column("tenant_id", _UUID, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("matter_number", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("matter_type", sa.String(64), nullable=False),
        sa.Column("court_system", sa.String(64), nullable=False),
        sa.Column("court_name", sa.String(255)),
        sa.Column("case_reference", sa.String(128)),
        sa.Column("role_in_case", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="OPEN"),
        sa.Column("risk_level", sa.String(32), nullable=False, server_default="MEDIUM"),
        sa.Column("business_unit", sa.String(128)),
        sa.Column("owner_user_id", _UUID, sa.ForeignKey("api_users.id")),
        sa.Column("outside_counsel_required", sa.Boolean, server_default=sa.text("false")),
        sa.Column("estimated_exposure", sa.Numeric(18, 2)),
        sa.Column("currency", sa.String(3)),
        sa.Column("opened_at", _TS, server_default=sa.func.now()),
        sa.Column("closed_at", _TS),
        sa.Column("metadata", _JSONB, server_default="{}"),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
        sa.Column("updated_at", _TS, server_default=sa.func.now()),
    )
    op.create_index("idx_matters_status", "matters", ["tenant_id", "status"])
    op.create_index("idx_matters_owner", "matters", ["owner_user_id", "status"])

    # ── Matter Parties ─────────────────────────────────────
    op.create_table(
        "matter_parties",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("party_role", sa.String(32), nullable=False),
        sa.Column("legal_name", sa.String(255), nullable=False),
        sa.Column("inn", sa.String(12)),
        sa.Column("ogrn", sa.String(15)),
        sa.Column("representative_name", sa.String(255)),
        sa.Column("metadata", _JSONB, server_default="{}"),
    )

    # ── Hearings ───────────────────────────────────────────
    op.create_table(
        "hearings",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("hearing_type", sa.String(64), nullable=False),
        sa.Column("scheduled_at", _TS, nullable=False),
        sa.Column("courtroom", sa.String(128)),
        sa.Column("judge_name", sa.String(255)),
        sa.Column("status", sa.String(32), nullable=False, server_default="SCHEDULED"),
        sa.Column("outcome_summary", sa.Text),
        sa.Column("source_system", sa.String(64)),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
    )
    op.create_index("idx_hearings_scheduled", "hearings", ["scheduled_at", "status"])

    # ── Procedural Deadlines ───────────────────────────────
    op.create_table(
        "procedural_deadlines",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("deadline_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("due_at", _TS, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="OPEN"),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("priority", sa.String(32), nullable=False, server_default="NORMAL"),
        sa.Column("assigned_user_id", _UUID, sa.ForeignKey("api_users.id")),
        sa.Column("escalation_at", _TS),
        sa.Column("completed_at", _TS),
        sa.Column("metadata", _JSONB, server_default="{}"),
    )
    op.create_index("idx_deadlines_due", "procedural_deadlines", ["due_at", "status"])

    # ── Evidence Items ─────────────────────────────────────
    op.create_table(
        "evidence_items",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(128), nullable=False),
        sa.Column("storage_path", sa.String(512), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("evidence_type", sa.String(64), nullable=False),
        sa.Column("privilege_level", sa.String(32), nullable=False, server_default="STANDARD"),
        sa.Column("source_description", sa.Text),
        sa.Column("admissibility_note", sa.Text),
        sa.Column("uploaded_by", _UUID, sa.ForeignKey("api_users.id"), nullable=False),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
    )

    # ── Issues ─────────────────────────────────────────────
    op.create_table(
        "issues",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("severity", sa.String(32), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(32), nullable=False, server_default="OPEN"),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
    )

    # ── Claims ─────────────────────────────────────────────
    op.create_table(
        "claims",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2)),
        sa.Column("currency", sa.String(3)),
        sa.Column("status", sa.String(32), nullable=False, server_default="OPEN"),
        sa.Column("metadata", _JSONB, server_default="{}"),
    )

    # ── Defenses ───────────────────────────────────────────
    op.create_table(
        "defenses",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("strategy_note", sa.Text),
    )

    # ── Chronology Events ──────────────────────────────────
    op.create_table(
        "chronology_events",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_at", _TS, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("source_id", _UUID),
        sa.Column("ai_generated", sa.Boolean, server_default=sa.text("false")),
        sa.Column("confidence", sa.Numeric(4, 3)),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
    )

    # ── Outside Counsel ────────────────────────────────────
    op.create_table(
        "outside_counsel_assignments",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("firm_name", sa.String(255), nullable=False),
        sa.Column("lead_lawyer", sa.String(255)),
        sa.Column("scoped_access", _JSONB, server_default="[]"),
        sa.Column("engagement_terms", _JSONB, server_default="{}"),
        sa.Column("started_at", _TS, server_default=sa.func.now()),
        sa.Column("ended_at", _TS),
    )

    # ── Budget Entries ─────────────────────────────────────
    op.create_table(
        "budget_entries",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entry_type", sa.String(32), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("vendor_name", sa.String(255)),
        sa.Column("description", sa.Text),
        sa.Column("incurred_at", _TS, nullable=False),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
    )

    # ── Review Notes ───────────────────────────────────────
    op.create_table(
        "review_notes",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("author_user_id", _UUID, sa.ForeignKey("api_users.id"), nullable=False),
        sa.Column("note_type", sa.String(32), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column(
            "related_deadline_id",
            _UUID,
            sa.ForeignKey("procedural_deadlines.id"),
        ),
        sa.Column("related_hearing_id", _UUID, sa.ForeignKey("hearings.id")),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
    )

    # ── Alerts ─────────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("alert_type", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("acknowledged", sa.Boolean, server_default=sa.text("false")),
        sa.Column("acknowledged_by", _UUID, sa.ForeignKey("api_users.id")),
        sa.Column("acknowledged_at", _TS),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
    )
    op.create_index("idx_alerts_ack", "alerts", ["acknowledged", "created_at"])

    # ── AI Analysis Runs ───────────────────────────────────
    op.create_table(
        "ai_analysis_runs",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column(
            "matter_id",
            _UUID,
            sa.ForeignKey("matters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("pipeline_type", sa.String(64), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("prompt_hash", sa.String(64), nullable=False),
        sa.Column("prompt_version", sa.String(32), nullable=False),
        sa.Column("input_snapshot", _JSONB, nullable=False),
        sa.Column("output_snapshot", _JSONB, nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("latency_ms", sa.Integer),
        sa.Column("prompt_tokens", sa.Integer),
        sa.Column("completion_tokens", sa.Integer),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
    )
    op.create_index("idx_ai_runs_matter", "ai_analysis_runs", ["matter_id", "created_at"])

    # ── Audit Events ───────────────────────────────────────
    op.create_table(
        "audit_events",
        sa.Column("id", _UUID, primary_key=True),
        sa.Column("tenant_id", _UUID, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("actor_user_id", _UUID, sa.ForeignKey("api_users.id")),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", _UUID, nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("trace_id", sa.String(128)),
        sa.Column("payload", _JSONB, server_default="{}"),
        sa.Column("created_at", _TS, server_default=sa.func.now()),
    )
    op.create_index(
        "idx_audit_resource",
        "audit_events",
        ["resource_type", "resource_id", "created_at"],
    )


def downgrade() -> None:
    tables = [
        "audit_events",
        "ai_analysis_runs",
        "alerts",
        "review_notes",
        "budget_entries",
        "outside_counsel_assignments",
        "chronology_events",
        "defenses",
        "claims",
        "issues",
        "evidence_items",
        "procedural_deadlines",
        "hearings",
        "matter_parties",
        "matters",
        "api_users",
        "tenants",
    ]
    for table in tables:
        op.drop_table(table)
