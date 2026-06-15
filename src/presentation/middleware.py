from __future__ import annotations

import time
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    DuplicateError,
    InvalidStateTransitionError,
    NotFoundError,
)

logger = structlog.get_logger("middleware")


class RequestContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.monotonic()
        response = await call_next(request)
        elapsed_ms = round((time.monotonic() - start) * 1000, 2)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(elapsed_ms)

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            elapsed_ms=elapsed_ms,
        )
        return response


def register_exception_handlers(app: FastAPI) -> None:

    from fastapi.responses import ORJSONResponse

    @app.exception_handler(NotFoundError)
    async def _not_found(request: Request, exc: NotFoundError) -> ORJSONResponse:
        return ORJSONResponse({"detail": exc.message}, status_code=404)

    @app.exception_handler(DuplicateError)
    async def _duplicate(request: Request, exc: DuplicateError) -> ORJSONResponse:
        return ORJSONResponse({"detail": exc.message}, status_code=409)

    @app.exception_handler(AuthenticationError)
    async def _authn(request: Request, exc: AuthenticationError) -> ORJSONResponse:
        return ORJSONResponse({"detail": exc.message}, status_code=401)

    @app.exception_handler(AuthorizationError)
    async def _authz(request: Request, exc: AuthorizationError) -> ORJSONResponse:
        return ORJSONResponse({"detail": exc.message}, status_code=403)

    @app.exception_handler(InvalidStateTransitionError)
    async def _bad_transition(
        request: Request, exc: InvalidStateTransitionError
    ) -> ORJSONResponse:
        return ORJSONResponse({"detail": exc.message}, status_code=422)

    @app.exception_handler(DomainError)
    async def _domain(request: Request, exc: DomainError) -> ORJSONResponse:
        return ORJSONResponse({"detail": exc.message}, status_code=400)
