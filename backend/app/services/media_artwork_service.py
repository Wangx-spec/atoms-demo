from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import MediaArtworkORM, UserORM
from app.repositories.media_artworks import MediaArtworkRepository
from app.repositories.tasks import TaskRepository
from app.schemas.media_artworks import MediaArtworkResponse, SaveTaskAsArtworkRequest
from app.services.storage_service import storage_service


MEDIA_TASK_TYPES = {
    "image_generation": "image",
    "music_generation": "music",
}


class MediaArtworkService:
    def __init__(self, db: AsyncSession) -> None:
        self.artworks = MediaArtworkRepository(db)
        self.tasks = TaskRepository(db)

    async def save_from_task(
        self, user: UserORM, task_id: UUID, payload: SaveTaskAsArtworkRequest
    ) -> MediaArtworkResponse:
        task = await self.tasks.get(task_id)
        if not task or task.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        artwork_type = MEDIA_TASK_TYPES.get(task.type)
        if not artwork_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image and music tasks can be saved as artworks",
            )
        if task.status != "succeeded":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only succeeded tasks can be saved as artworks",
            )

        result_meta = task.result_meta or {}
        object_key = result_meta.get("object_key")
        if not object_key:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task has no generated media object",
            )

        existing = await self.artworks.get_by_task(task.id)
        if existing:
            return self._to_response(existing)

        artwork = await self.artworks.create(
            user_id=user.id,
            source_task_id=task.id,
            type=artwork_type,
            prompt=task.params.get("prompt", ""),
            title=payload.title,
            params=task.params or {},
            object_key=object_key,
            content_type=result_meta.get("content_type", "application/octet-stream"),
            visibility=payload.visibility,
        )
        return self._to_response(artwork)

    async def list_artworks(self, user: UserORM) -> list[MediaArtworkResponse]:
        artworks = await self.artworks.list_by_user(user.id)
        return [self._to_response(artwork) for artwork in artworks]

    async def delete_artwork(self, user: UserORM, artwork_id: UUID) -> None:
        artwork = await self._get_owned_artwork(user, artwork_id)
        await self.artworks.delete(artwork)

    async def _get_owned_artwork(self, user: UserORM, artwork_id: UUID) -> MediaArtworkORM:
        artwork = await self.artworks.get(artwork_id)
        if not artwork or artwork.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media artwork not found"
            )
        return artwork

    @staticmethod
    def _to_response(artwork: MediaArtworkORM) -> MediaArtworkResponse:
        response = MediaArtworkResponse.model_validate(artwork, from_attributes=True)
        try:
            response.media_url = storage_service.presigned_url(artwork.object_key)
        except Exception:
            response.media_url = None
        return response
