from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

MATTERS_TOTAL = Counter(
    "litigation_matters_total",
    "Total matters created",
    ["tenant_id", "matter_type"],
)
OPEN_MATTERS = Gauge(
    "litigation_open_matters_total",
    "Currently open matters",
    ["tenant_id"],
)

DEADLINES_OVERDUE = Gauge(
    "litigation_deadlines_overdue_total",
    "Currently overdue deadlines",
    ["tenant_id"],
)
DEADLINES_DUE_72H = Gauge(
    "litigation_deadlines_due_72h_total",
    "Deadlines due within 72 hours",
    ["tenant_id"],
)

HEARINGS_UPCOMING = Gauge(
    "litigation_hearings_upcoming_total",
    "Hearings scheduled in the next 7 days",
    ["tenant_id"],
)

AI_RUNS_TOTAL = Counter(
    "litigation_ai_runs_total",
    "Total AI pipeline runs",
    ["pipeline_type"],
)
AI_FAILURES = Counter(
    "litigation_ai_failures_total",
    "Failed AI pipeline runs",
    ["pipeline_type"],
)
AI_PIPELINE_DURATION = Histogram(
    "litigation_ai_pipeline_duration_seconds",
    "AI pipeline latency",
    ["pipeline_type"],
    buckets=[1, 5, 10, 30, 60, 120],
)

ALERTS_TOTAL = Counter(
    "litigation_alerts_total",
    "Total alerts created",
    ["alert_type", "severity"],
)

OUTSIDE_COUNSEL_SPEND = Gauge(
    "litigation_outside_counsel_spend_total",
    "Total outside counsel spend",
    ["tenant_id", "currency"],
)

CHRONOLOGY_EVENTS = Counter(
    "litigation_chronology_events_total",
    "Total chronology events generated",
    ["source_type"],
)

DEADLINE_SCAN_DURATION = Histogram(
    "litigation_deadline_scan_duration_seconds",
    "Deadline risk scan duration",
    buckets=[0.5, 1, 2, 5, 10],
)
CASE_IMPORT_DURATION = Histogram(
    "litigation_case_import_duration_seconds",
    "Court case import duration",
    buckets=[1, 5, 10, 30, 60],
)
PORTFOLIO_REFRESH_DURATION = Histogram(
    "litigation_portfolio_refresh_duration_seconds",
    "Portfolio analytics refresh duration",
    buckets=[1, 5, 10, 30],
)
