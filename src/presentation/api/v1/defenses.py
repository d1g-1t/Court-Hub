from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from src.application.dto import CreateDefenseRequest, DefenseResponse
from src.application.use_cases.crud import create_defense, list_matter_defenses
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.post("/matters/{matter_id}", response_model=DefenseResponse, status_code=201)
async def create(
    matter_id: UUID,
    body: CreateDefenseRequest,
    auth: AuthDep,
    session: SessionDep,
) -> DefenseResponse:
    defense = await create_defense(matter_id, body, session=session)
    return DefenseResponse.model_validate(defense)


@router.get("/matters/{matter_id}", response_model=list[DefenseResponse])
async def list_defenses(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> list[DefenseResponse]:
    items = await list_matter_defenses(matter_id, session=session)
    return [DefenseResponse.model_validate(d) for d in items]
