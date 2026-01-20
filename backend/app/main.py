from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.concepts import router as concepts_router
from app.api.routes.health import router as health_router
from app.api.routes.progress import router as progress_router
from app.api.routes.practice import router as practice_router
from app.api.routes.questions import router as questions_router
from app.core.settings import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance.

    Notes:
        We use an application factory to keep startup behavior testable.
    """

    settings = get_settings()

    app = FastAPI(title=settings.app_name)

    allow_origins = [origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.include_router(health_router)
    app.include_router(concepts_router)
    app.include_router(progress_router)
    app.include_router(practice_router)
    app.include_router(questions_router)

    return app


app = create_app()
