import asyncio
import contextlib
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    admin,
    agent,
    apps,
    auth,
    billing,
    discovery,
    gallery,
    media_artworks,
    payments,
    sandbox,
    tasks,
    ws,
)
from app.core.config import settings
from app.core.rate_limit import setup_rate_limiting
from app.core.telemetry import setup_metrics, setup_tracing
from app.services.sandbox_service import sandbox_service


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    reaper = asyncio.create_task(sandbox_service.reap_loop())
    try:
        yield
    finally:
        reaper.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await reaper


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def limit_upload_size(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_upload_mb * 1024 * 1024:
            return JSONResponse(status_code=413, content={"detail": "Payload too large"})
        return await call_next(request)

    setup_rate_limiting(app)
    setup_metrics(app)
    setup_tracing(app)

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
    app.include_router(apps.router, prefix="/api/apps", tags=["apps"])
    app.include_router(sandbox.router, prefix="/api/apps", tags=["sandbox"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
    app.include_router(media_artworks.router, prefix="/api/media-artworks", tags=["media-artworks"])
    app.include_router(gallery.router, prefix="/api/gallery", tags=["gallery"])
    app.include_router(gallery.profiles_router, prefix="/api/users", tags=["users"])
    app.include_router(discovery.router, prefix="/api", tags=["discovery"])
    app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
    app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
    app.include_router(ws.router, prefix="/ws", tags=["websocket"])

    @app.get("/api/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return app


app = create_app()
