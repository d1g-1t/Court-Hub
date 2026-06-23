from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from src.application.dto import CreateIssueRequest, IssueResponse, UpdateIssueRequest
from src.application.use_cases.crud import create_issue, list_matter_issues, update_issue
from src.presentation.deps import AuthDep, SessionDep

router = APIRouter()


@router.post("/matters/{matter_id}", response_model=IssueResponse, status_code=201)
async def create(
    matter_id: UUID,
    body: CreateIssueRequest,
    auth: AuthDep,
    session: SessionDep,
) -> IssueResponse:
    issue = await create_issue(matter_id, body, session=session)
    return IssueResponse.model_validate(issue)


@router.get("/matters/{matter_id}", response_model=list[IssueResponse])
async def list_issues(
    matter_id: UUID,
    auth: AuthDep,
    session: SessionDep,
) -> list[IssueResponse]:
    items = await list_matter_issues(matter_id, session=session)
    return [IssueResponse.model_validate(i) for i in items]


@router.patch("/{issue_id}", response_model=IssueResponse)
async def update(
    issue_id: UUID,
    body: UpdateIssueRequest,
    auth: AuthDep,
    session: SessionDep,
) -> IssueResponse:
    issue = await update_issue(issue_id, body, session=session)
    return IssueResponse.model_validate(issue)
