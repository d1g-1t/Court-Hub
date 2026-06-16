from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from src.application.dto import AIRunResponse
from src.application.use_cases.ai_operations import run_ai_pipeline
from src.presentation.deps import AuthDep, SessionDep, SettingsDep

router = APIRouter()


@router.post("/matters/{matter_id}/summary", response_model=AIRunResponse)
async def case_summary(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
    settings: SettingsDep,
) -> AIRunResponse:
    run = await run_ai_pipeline(
        matter_id, "CASE_SUMMARY", session=session, settings=settings
    )
    return AIRunResponse.model_validate(run)


@router.post("/matters/{matter_id}/hearing-memo", response_model=AIRunResponse)
async def hearing_memo(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
    settings: SettingsDep,
) -> AIRunResponse:
    run = await run_ai_pipeline(
        matter_id, "HEARING_MEMO", session=session, settings=settings
    )
    return AIRunResponse.model_validate(run)


@router.post("/matters/{matter_id}/risk-review", response_model=AIRunResponse)
async def risk_review(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
    settings: SettingsDep,
) -> AIRunResponse:
    run = await run_ai_pipeline(
        matter_id, "RISK_REVIEW", session=session, settings=settings
    )
    return AIRunResponse.model_validate(run)


@router.post("/matters/{matter_id}/inconsistency-check", response_model=AIRunResponse)
async def inconsistency_check(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
    settings: SettingsDep,
) -> AIRunResponse:
    run = await run_ai_pipeline(
        matter_id, "INCONSISTENCY_DETECTION", session=session, settings=settings
    )
    return AIRunResponse.model_validate(run)
