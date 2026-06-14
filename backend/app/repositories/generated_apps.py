from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import GeneratedAppORM


class GeneratedAppRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **fields) -> GeneratedAppORM:
        app = GeneratedAppORM(**fields)
        self.db.add(app)
        await self.db.commit()
        await self.db.refresh(app)
        return app

    async def get(self, app_id: UUID) -> GeneratedAppORM | None:
        return await self.db.get(GeneratedAppORM, app_id)

    async def list_by_user(self, user_id: UUID) -> list[GeneratedAppORM]:
        result = await self.db.execute(
            select(GeneratedAppORM)
            .where(GeneratedAppORM.user_id == user_id)
            .order_by(GeneratedAppORM.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, app: GeneratedAppORM, data: dict) -> GeneratedAppORM:
        for key, value in data.items():
            setattr(app, key, value)
        await self.db.commit()
        await self.db.refresh(app)
        return app

    async def delete(self, app: GeneratedAppORM) -> None:
        await self.db.delete(app)
        await self.db.commit()
