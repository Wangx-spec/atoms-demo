from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import AgentSessionORM


class AgentSessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, user_id: UUID, title: str) -> AgentSessionORM:
        session = AgentSessionORM(user_id=user_id, title=title, messages=[], context={})
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get(self, session_id: UUID) -> AgentSessionORM | None:
        return await self.db.get(AgentSessionORM, session_id)

    async def list_by_user(self, user_id: UUID) -> list[AgentSessionORM]:
        result = await self.db.execute(
            select(AgentSessionORM)
            .where(AgentSessionORM.user_id == user_id)
            .order_by(AgentSessionORM.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, session: AgentSessionORM, data: dict) -> AgentSessionORM:
        for key, value in data.items():
            setattr(session, key, value)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def append_message(self, session: AgentSessionORM, message: dict) -> AgentSessionORM:
        session.messages = [*session.messages, message]
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def delete(self, session: AgentSessionORM) -> None:
        await self.db.delete(session)
        await self.db.commit()
