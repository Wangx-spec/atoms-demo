from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import GeneratedAppFileORM


class GeneratedAppFileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_app(self, app_id: UUID) -> list[GeneratedAppFileORM]:
        result = await self.db.execute(
            select(GeneratedAppFileORM).where(GeneratedAppFileORM.app_id == app_id)
        )
        return list(result.scalars().all())

    async def replace_all(self, app_id: UUID, files: dict[str, str]) -> None:
        await self.db.execute(
            delete(GeneratedAppFileORM).where(GeneratedAppFileORM.app_id == app_id)
        )
        for path, content in files.items():
            self.db.add(GeneratedAppFileORM(app_id=app_id, path=path, content=content))
        await self.db.commit()
