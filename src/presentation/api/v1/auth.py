"""Auth endpoints — login, refresh, me."""

from __future__ import annotations

from fastapi import APIRouter

from src.application.dto import (
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from src.application.use_cases import auth as auth_uc
from src.presentation.deps import AuthDep, SessionDep, SettingsDep

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> TokenResponse:
    result = await auth_uc.login(
        body.email, body.password, session=session, settings=settings
    )
    return TokenResponse(**result)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> TokenResponse:
    result = await auth_uc.refresh_tokens(
        body.refresh_token, session=session, settings=settings
    )
    return TokenResponse(**result)


@router.get("/me", response_model=UserResponse)
async def me(
    auth: AuthDep,
    session: SessionDep,
) -> UserResponse:
    user = await auth_uc.get_current_user(auth.user_id, session=session)
    return UserResponse.model_validate(user)
