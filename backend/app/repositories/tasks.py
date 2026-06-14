from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import TaskORM


class TaskRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **fields) -> TaskORM:
        task = TaskORM(**fields)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get(self, task_id: UUID) -> TaskORM | None:
        return await self.db.get(TaskORM, task_id)

    async def list_by_user(self, user_id: UUID) -> list[TaskORM]:
        result = await self.db.execute(
            select(TaskORM)
            .where(TaskORM.user_id == user_id)
            .order_by(TaskORM.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, task: TaskORM, data: dict) -> TaskORM:
        for key, value in data.items():
            setattr(task, key, value)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task: TaskORM) -> None:
        await self.db.delete(task)
        await self.db.commit()
