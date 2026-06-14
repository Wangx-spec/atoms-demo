"""Billing: credit accounting for paid actions.

``charge`` debits a user's credits and writes a transaction; raises HTTP 402 when
the balance is insufficient. ``credit`` adds credits (e.g. on plan purchase).
"""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.db import UserORM
from app.repositories.billing import BillingRepository

COST_BY_TYPE = {
    "code_generation": settings.credit_cost_code,
    "image_generation": settings.credit_cost_image,
    "music_generation": settings.credit_cost_music,
    "preview_snapshot": 0,
}


class BillingService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = BillingRepository(db)

    def cost_for(self, task_type: str) -> int:
        return COST_BY_TYPE.get(task_type, 0)

    async def charge(self, user: UserORM, amount: int, reason: str, ref: str | None = None) -> None:
        if amount <= 0:
            return
        if user.credits < amount:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Insufficient credits"
            )
        user.credits -= amount
        await self.repo.add_transaction(user.id, -amount, user.credits, reason, ref)
        await self.repo.record_usage(user.id, reason, datetime.now(UTC).strftime("%Y-%m-%d"))

    async def credit(self, user: UserORM, amount: int, reason: str, ref: str | None = None) -> None:
        if amount <= 0:
            return
        user.credits += amount
        await self.repo.add_transaction(user.id, amount, user.credits, reason, ref)
