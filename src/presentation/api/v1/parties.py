from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from src.application.dto import CreatePartyRequest, PartyResponse, UpdatePartyRequest
from src.domain.exceptions import NotFoundError
from src.infrastructure.database.models import MatterPartyModel
from src.infrastructure.database.repositories import MatterSQLRepository, PartySQLRepository
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.post("/matters/{matter_id}", response_model=PartyResponse, status_code=201)
async def add_party(
    matter_id: UUID,
    body: CreatePartyRequest,
    auth: AuthDep,
    session: SessionDep,
) -> PartyResponse:
    matter_repo = MatterSQLRepository(session)
    if not await matter_repo.get_by_id(matter_id):
        raise NotFoundError("Matter", matter_id)

    repo = PartySQLRepository(session)
    party = MatterPartyModel(
        matter_id=matter_id,
        party_role=body.party_role,
        legal_name=body.legal_name,
        inn=body.inn,
        ogrn=body.ogrn,
        representative_name=body.representative_name,
    )
    party = await repo.create(party)
    return PartyResponse.model_validate(party)


@router.patch("/{party_id}", response_model=PartyResponse)
async def update_party(
    party_id: UUID,
    body: UpdatePartyRequest,
    auth: AuthDep,
    session: SessionDep,
) -> PartyResponse:
    repo = PartySQLRepository(session)
    party = await repo.get_by_id(party_id)
    if not party:
        raise NotFoundError("Party", party_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(party, k, v)
    party = await repo.update(party)
    return PartyResponse.model_validate(party)


@router.delete("/{party_id}", status_code=204)
async def delete_party(
    party_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> None:
    repo = PartySQLRepository(session)
    await repo.delete(party_id)
