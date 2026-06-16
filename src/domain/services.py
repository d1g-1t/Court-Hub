from __future__ import annotations

from datetime import UTC, datetime, timedelta

from src.domain.entities import Alert, AuditEvent, ProceduralDeadline
from src.domain.exceptions import InvalidStateTransitionError
from src.domain.value_objects import (
    AlertSeverity,
    AlertType,
    AuditEventType,
    DeadlineStatus,
    MatterStatus,
)

_MATTER_TRANSITIONS: dict[MatterStatus, set[MatterStatus]] = {
    MatterStatus.OPEN: {MatterStatus.IN_PROGRESS, MatterStatus.ON_HOLD, MatterStatus.CLOSED},
    MatterStatus.IN_PROGRESS: {
        MatterStatus.ON_HOLD,
        MatterStatus.SETTLED,
        MatterStatus.WON,
        MatterStatus.LOST,
        MatterStatus.CLOSED,
    },
    MatterStatus.ON_HOLD: {MatterStatus.OPEN, MatterStatus.IN_PROGRESS, MatterStatus.CLOSED},
    MatterStatus.SETTLED: {MatterStatus.CLOSED},
    MatterStatus.WON: {MatterStatus.CLOSED},
    MatterStatus.LOST: {MatterStatus.CLOSED},
    MatterStatus.CLOSED: set(),
}


def validate_matter_transition(current: MatterStatus, target: MatterStatus) -> None:
    if target not in _MATTER_TRANSITIONS.get(current, set()):
        raise InvalidStateTransitionError("Matter", current, target)


def build_audit_event(
    *,
    tenant_id: "from uuid import UUID",
    actor_user_id: "UUID | None" = None,
    resource_type: str,
    resource_id: "UUID",
    event_type: AuditEventType,
    payload: dict | None = None,
) -> AuditEvent:
    from uuid import UUID as _UUID

    return AuditEvent(
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        event_type=event_type,
        payload=payload or {},
        created_at=datetime.now(UTC),
    )


def evaluate_deadline_risk(
    deadline: ProceduralDeadline,
    *,
    warning_hours: int = 72,
    critical_hours: int = 24,
) -> Alert | None:
    if deadline.status != DeadlineStatus.OPEN or deadline.due_at is None:
        return None

    now = datetime.now(UTC)
    remaining = deadline.due_at - now

    if remaining < timedelta(0):
        return Alert(
            matter_id=deadline.matter_id,
            alert_type=AlertType.DEADLINE_OVERDUE,
            severity=AlertSeverity.CRITICAL,
            title=f"Overdue: {deadline.title}",
            message=f"Deadline '{deadline.title}' was due at {deadline.due_at.isoformat()}.",
            created_at=now,
        )

    if remaining < timedelta(hours=critical_hours):
        return Alert(
            matter_id=deadline.matter_id,
            alert_type=AlertType.DEADLINE_WARNING,
            severity=AlertSeverity.HIGH,
            title=f"Critical: {deadline.title}",
            message=(
                f"Deadline '{deadline.title}' is due in "
                f"{remaining.total_seconds() / 3600:.1f} hours."
            ),
            created_at=now,
        )

    if remaining < timedelta(hours=warning_hours):
        return Alert(
            matter_id=deadline.matter_id,
            alert_type=AlertType.DEADLINE_WARNING,
            severity=AlertSeverity.WARNING,
            title=f"Approaching: {deadline.title}",
            message=(
                f"Deadline '{deadline.title}' is due in "
                f"{remaining.total_seconds() / 3600:.1f} hours."
            ),
            created_at=now,
        )

    return None
