from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import GeneratedAppORM, UserORM
from app.repositories.generated_apps import GeneratedAppRepository
from app.schemas.apps import (
    GeneratedAppResponse,
    SaveGeneratedAppRequest,
    UpdateGeneratedAppRequest,
)


class AppService:
    def __init__(self, db: AsyncSession) -> None:
        self.apps = GeneratedAppRepository(db)

    async def save_app(
        self, user: UserORM, payload: SaveGeneratedAppRequest
    ) -> GeneratedAppResponse:
        app = await self.apps.create(
            user_id=user.id,
            session_id=payload.session_id,
            prompt=payload.prompt,
            html=payload.html,
            css=payload.css,
            js=payload.js,
            status=payload.status,
            runtime=payload.runtime,
        )
        return GeneratedAppResponse.model_validate(app, from_attributes=True)

    async def list_apps(self, user: UserORM) -> list[GeneratedAppResponse]:
        apps = await self.apps.list_by_user(user.id)
        return [GeneratedAppResponse.model_validate(app, from_attributes=True) for app in apps]

    async def get_app(self, user: UserORM, app_id: UUID) -> GeneratedAppResponse:
        app = await self._get_owned_app(user, app_id)
        return GeneratedAppResponse.model_validate(app, from_attributes=True)

    async def update_app(
        self, user: UserORM, app_id: UUID, payload: UpdateGeneratedAppRequest
    ) -> GeneratedAppResponse:
        from datetime import UTC, datetime

        app = await self._get_owned_app(user, app_id)
        data = payload.model_dump(exclude_unset=True)
        going_public = data.get("visibility") == "public" and app.visibility != "public"
        if going_public:
            data["published_at"] = datetime.now(UTC)
        updated = await self.apps.update(app, data)
        if going_public:
            self._trigger_embedding(updated.id)
        return GeneratedAppResponse.model_validate(updated, from_attributes=True)

    def _trigger_embedding(self, app_id: UUID) -> None:
        """Best-effort: enqueue vectorization of a newly public artwork."""
        try:
            from app.workers.celery_app import celery_app

            if celery_app is not None:
                celery_app.send_task("embed_artwork", args=[str(app_id)])
                return
        except Exception:
            pass
        try:
            import asyncio

            from app.services.vector_service import run_embed_artwork

            asyncio.create_task(run_embed_artwork(app_id))
        except Exception:
            pass

    async def delete_app(self, user: UserORM, app_id: UUID) -> None:
        app = await self._get_owned_app(user, app_id)
        await self.apps.delete(app)

    async def _get_owned_app(self, user: UserORM, app_id: UUID) -> GeneratedAppORM:
        app = await self.apps.get(app_id)
        if not app or app.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App not found")
        return app
