from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.core.config import Settings
from src.core.logging import setup_logging
from src.presentation.api.v1.router import api_v1_router
from src.presentation.deps import close_deps, init_deps
from src.presentation.middleware import (
    RequestContextMiddleware,
    register_exception_handlers,
)

logger = structlog.get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:

    settings = Settings()

    json_logs = settings.app_env != "dev"
    setup_logging(log_level=settings.app_log_level, json_output=json_logs)

    init_deps(settings)

    logger.info(
        "startup",
        env=settings.app_env,
        port=settings.app_port,
        db_host=settings.postgres_host,
        redis_host=settings.redis_host,
    )

    yield

    await close_deps()
    logger.info("shutdown_complete")


def create_app() -> FastAPI:

    settings = Settings()

    app = FastAPI(
        title=settings.app_title,
        version="0.1.0",
        description=(
            "Enterprise litigation operations platform — "
            "matter management, procedural deadlines, AI case intelligence, "
            "outside counsel oversight, and portfolio analytics."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)

    app.include_router(api_v1_router)

    return app


app = create_app()
