from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import UserORM


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: UUID) -> UserORM | None:
        return await self.db.get(UserORM, user_id)

    async def get_by_email(self, email: str) -> UserORM | None:
        result = await self.db.execute(select(UserORM).where(UserORM.email == email))
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str) -> UserORM:
        user = UserORM(email=email, password_hash=password_hash)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
