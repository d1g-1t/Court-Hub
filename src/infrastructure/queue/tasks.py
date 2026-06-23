from __future__ import annotations

import structlog

from src.infrastructure.queue.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="src.infrastructure.queue.tasks.import_court_case_task", bind=True)
def import_court_case_task(self, case_reference: str, court_system: str) -> dict:
    logger.info(
        "import_court_case_started",
        case_reference=case_reference,
        court_system=court_system,
    )
    return {
        "status": "imported",
        "case_reference": case_reference,
        "court_system": court_system,
    }


@celery_app.task(name="src.infrastructure.queue.tasks.sync_hearings_task", bind=True)
def sync_hearings_task(self, matter_id: str) -> dict:
    logger.info("sync_hearings_started", matter_id=matter_id)
    return {"status": "synced", "matter_id": matter_id}


@celery_app.task(name="src.infrastructure.queue.tasks.generate_chronology_task", bind=True)
def generate_chronology_task(self, matter_id: str) -> dict:
    logger.info("generate_chronology_started", matter_id=matter_id)
    return {"status": "generated", "matter_id": matter_id}


@celery_app.task(name="src.infrastructure.queue.tasks.run_inconsistency_check_task", bind=True)
def run_inconsistency_check_task(self, matter_id: str) -> dict:
    logger.info("inconsistency_check_started", matter_id=matter_id)
    return {"status": "checked", "matter_id": matter_id}


@celery_app.task(name="src.infrastructure.queue.tasks.deadline_risk_scan_task", bind=True)
def deadline_risk_scan_task(self) -> dict:
    logger.info("deadline_risk_scan_started")
    return {"status": "scanned"}


@celery_app.task(name="src.infrastructure.queue.tasks.portfolio_analytics_task", bind=True)
def portfolio_analytics_task(self) -> dict:
    logger.info("portfolio_analytics_started")
    return {"status": "refreshed"}


@celery_app.task(
    name="src.infrastructure.queue.tasks.outside_counsel_spend_rollup_task", bind=True
)
def outside_counsel_spend_rollup_task(self) -> dict:
    logger.info("spend_rollup_started")
    return {"status": "rolled_up"}
