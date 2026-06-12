from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent, apps, auth, tasks, ws
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
    app.include_router(apps.router, prefix="/api/apps", tags=["apps"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
    app.include_router(ws.router, prefix="/ws", tags=["websocket"])

    @app.get("/api/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return app


app = create_app()
