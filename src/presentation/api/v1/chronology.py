from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from src.application.dto import ChronologyEventResponse, GenerateChronologyRequest
from src.application.use_cases.ai_operations import generate_chronology, list_chronology
from src.presentation.deps import AuthDep, SessionDep, SettingsDep

router = APIRouter()


@router.post(
    "/matters/{matter_id}/generate",
    response_model=list[ChronologyEventResponse],
    status_code=201,
)
async def generate(
    matter_id: UUID,
    body: GenerateChronologyRequest,
    auth: AuthDep,
    session: SessionDep,
    settings: SettingsDep,
) -> list[ChronologyEventResponse]:
    events = await generate_chronology(
        matter_id,
        session=session,
        settings=settings,
        min_confidence=body.min_confidence,
    )
    return [ChronologyEventResponse.model_validate(e) for e in events]


@router.get("/matters/{matter_id}", response_model=list[ChronologyEventResponse])
async def get_chronology(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> list[ChronologyEventResponse]:
    events = await list_chronology(matter_id, session=session)
    return [ChronologyEventResponse.model_validate(e) for e in events]
