from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from src.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "litigation_cc",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "src.infrastructure.queue.tasks.import_court_case_task": {"queue": "litigation.ingest"},
        "src.infrastructure.queue.tasks.sync_hearings_task": {"queue": "litigation.deadlines"},
        "src.infrastructure.queue.tasks.generate_chronology_task": {"queue": "litigation.ai"},
        "src.infrastructure.queue.tasks.run_inconsistency_check_task": {"queue": "litigation.ai"},
        "src.infrastructure.queue.tasks.deadline_risk_scan_task": {
            "queue": "litigation.monitoring"
        },
        "src.infrastructure.queue.tasks.portfolio_analytics_task": {
            "queue": "litigation.analytics"
        },
        "src.infrastructure.queue.tasks.outside_counsel_spend_rollup_task": {
            "queue": "litigation.analytics"
        },
    },
)

celery_app.conf.beat_schedule = {
    "deadline-risk-scan-every-15m": {
        "task": "src.infrastructure.queue.tasks.deadline_risk_scan_task",
        "schedule": crontab(minute="*/15"),
    },
    "portfolio-analytics-every-hour": {
        "task": "src.infrastructure.queue.tasks.portfolio_analytics_task",
        "schedule": crontab(minute=0),
    },
    "outside-counsel-spend-daily": {
        "task": "src.infrastructure.queue.tasks.outside_counsel_spend_rollup_task",
        "schedule": crontab(hour=2, minute=0),
    },
}

celery_app.autodiscover_tasks(["src.infrastructure.queue"])
