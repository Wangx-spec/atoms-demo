from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import CreditTransactionORM, PlanORM, SubscriptionORM, UsageStatORM


class BillingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add_transaction(
        self, user_id: UUID, amount: int, balance_after: int, reason: str, ref: str | None = None
    ) -> CreditTransactionORM:
        tx = CreditTransactionORM(
            user_id=user_id,
            amount=amount,
            balance_after=balance_after,
            reason=reason,
            ref=ref,
        )
        self.db.add(tx)
        await self.db.commit()
        await self.db.refresh(tx)
        return tx

    async def list_transactions(self, user_id: UUID, limit: int = 50) -> list[CreditTransactionORM]:
        result = await self.db.execute(
            select(CreditTransactionORM)
            .where(CreditTransactionORM.user_id == user_id)
            .order_by(CreditTransactionORM.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_plans(self) -> list[PlanORM]:
        result = await self.db.execute(select(PlanORM).order_by(PlanORM.price_cents))
        return list(result.scalars().all())

    async def get_plan_by_code(self, code: str) -> PlanORM | None:
        result = await self.db.execute(select(PlanORM).where(PlanORM.code == code))
        return result.scalar_one_or_none()

    async def create_subscription(self, user_id: UUID, plan_id: UUID) -> SubscriptionORM:
        sub = SubscriptionORM(user_id=user_id, plan_id=plan_id)
        self.db.add(sub)
        await self.db.commit()
        await self.db.refresh(sub)
        return sub

    async def record_usage(self, user_id: UUID, metric: str, day: str, value: int = 1) -> None:
        self.db.add(UsageStatORM(user_id=user_id, metric=metric, day=day, value=value))
        await self.db.commit()
