from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.db import UserORM
from app.repositories.generated_apps import GeneratedAppRepository
from app.services.sandbox_service import SandboxError, sandbox_service

router = APIRouter()


class SandboxResponse(BaseModel):
    app_id: str
    status: str
    runtime: str
    preview_url: str | None = None
    error: str | None = None


async def _owned_app(app_id: UUID, user: UserORM, db: AsyncSession):
    app = await GeneratedAppRepository(db).get(app_id)
    if not app or app.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App not found")
    return app


@router.post("/{app_id}/sandbox", response_model=SandboxResponse)
async def start_sandbox(
    app_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SandboxResponse:
    app = await _owned_app(app_id, current_user, db)
    try:
        instance = await sandbox_service.start(app)
    except SandboxError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return SandboxResponse(
        app_id=instance.app_id,
        status=instance.status,
        runtime=instance.runtime,
        preview_url=instance.preview_url,
    )


@router.get("/{app_id}/sandbox", response_model=SandboxResponse)
async def sandbox_status(
    app_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SandboxResponse:
    app = await _owned_app(app_id, current_user, db)
    instance = sandbox_service.get(str(app_id))
    if not instance:
        return SandboxResponse(
            app_id=str(app_id), status="stopped", runtime=getattr(app, "runtime", "static-html")
        )
    return SandboxResponse(
        app_id=instance.app_id,
        status=instance.status,
        runtime=instance.runtime,
        preview_url=instance.preview_url,
    )


@router.delete("/{app_id}/sandbox", status_code=status.HTTP_204_NO_CONTENT)
async def stop_sandbox(
    app_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await _owned_app(app_id, current_user, db)
    await sandbox_service.stop(str(app_id))


@router.get("/{app_id}/sandbox/logs")
async def sandbox_logs(
    app_id: UUID,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    await _owned_app(app_id, current_user, db)
    return {"logs": await sandbox_service.logs(str(app_id))}
