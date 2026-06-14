from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import MediaArtworkORM


class MediaArtworkRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **fields) -> MediaArtworkORM:
        artwork = MediaArtworkORM(**fields)
        self.db.add(artwork)
        await self.db.commit()
        await self.db.refresh(artwork)
        return artwork

    async def get(self, artwork_id: UUID) -> MediaArtworkORM | None:
        return await self.db.get(MediaArtworkORM, artwork_id)

    async def get_by_task(self, task_id: UUID) -> MediaArtworkORM | None:
        result = await self.db.execute(
            select(MediaArtworkORM).where(MediaArtworkORM.source_task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[MediaArtworkORM]:
        result = await self.db.execute(
            select(MediaArtworkORM)
            .where(MediaArtworkORM.user_id == user_id)
            .order_by(MediaArtworkORM.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, artwork: MediaArtworkORM) -> None:
        await self.db.delete(artwork)
        await self.db.commit()
