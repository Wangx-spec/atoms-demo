from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.db import UserORM
from app.repositories.billing import BillingRepository

router = APIRouter()


class TransactionItem(BaseModel):
    id: UUID
    amount: int
    balance_after: int
    reason: str
    ref: str | None = None
    created_at: datetime


class PlanItem(BaseModel):
    id: UUID
    code: str
    name: str
    price_cents: int
    credits: int
    period: str
    description: str | None = None


class BalanceResponse(BaseModel):
    credits: int


@router.get("/balance", response_model=BalanceResponse)
async def balance(current_user: UserORM = Depends(get_current_user)) -> BalanceResponse:
    return BalanceResponse(credits=current_user.credits)


@router.get("/transactions", response_model=list[TransactionItem])
async def transactions(
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TransactionItem]:
    items = await BillingRepository(db).list_transactions(current_user.id)
    return [TransactionItem.model_validate(t, from_attributes=True) for t in items]


@router.get("/plans", response_model=list[PlanItem])
async def plans(db: AsyncSession = Depends(get_db)) -> list[PlanItem]:
    items = await BillingRepository(db).list_plans()
    return [PlanItem.model_validate(p, from_attributes=True) for p in items]
