from __future__ import annotations

from fastapi import APIRouter

from src.presentation.api.v1 import (
    ai,
    alerts,
    analytics,
    audit,
    auth,
    budgets,
    chronology,
    claims,
    deadlines,
    defenses,
    evidence,
    health,
    hearings,
    issues,
    matters,
    outside_counsel,
    parties,
)

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health.router, prefix="/health", tags=["Health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(matters.router, prefix="/matters", tags=["Matters"])
api_v1_router.include_router(parties.router, prefix="/parties", tags=["Parties"])
api_v1_router.include_router(hearings.router, prefix="/hearings", tags=["Hearings"])
api_v1_router.include_router(deadlines.router, prefix="/deadlines", tags=["Deadlines"])
api_v1_router.include_router(evidence.router, prefix="/evidence", tags=["Evidence"])
api_v1_router.include_router(issues.router, prefix="/issues", tags=["Issues"])
api_v1_router.include_router(claims.router, prefix="/claims", tags=["Claims"])
api_v1_router.include_router(defenses.router, prefix="/defenses", tags=["Defenses"])
api_v1_router.include_router(chronology.router, prefix="/chronology", tags=["Chronology"])
api_v1_router.include_router(
    outside_counsel.router, prefix="/outside-counsel", tags=["Outside Counsel"]
)
api_v1_router.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
api_v1_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_v1_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_v1_router.include_router(audit.router, prefix="/audit", tags=["Audit"])
api_v1_router.include_router(ai.router, prefix="/ai", tags=["AI"])
