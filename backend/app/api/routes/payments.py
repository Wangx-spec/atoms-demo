"""Payment checkout + webhook placeholders.

Webhooks are public (no auth) but must verify provider signatures in production.
On a verified successful payment, credit the user's account / activate a plan.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.db import UserORM
from app.repositories.billing import BillingRepository
from app.services.payment.alipay_provider import get_payment_provider

router = APIRouter()


class CheckoutRequest(BaseModel):
    provider: str  # stripe | wechat | alipay
    plan_code: str


class CheckoutResponse(BaseModel):
    provider: str
    checkout_url: str
    session_id: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    payload: CheckoutRequest,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckoutResponse:
    plan = await BillingRepository(db).get_plan_by_code(payload.plan_code)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    try:
        provider = get_payment_provider(payload.provider)
        session = await provider.create_checkout(
            plan.code, plan.price_cents, str(current_user.id)
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return CheckoutResponse(
        provider=session.provider,
        checkout_url=session.checkout_url,
        session_id=session.session_id,
    )


@router.post("/webhook/{provider}")
async def payment_webhook(provider: str, request: Request) -> dict:
    """Receive provider callbacks. Verify signature, then fulfill the order.

    Placeholder: real impl looks up the order, credits the user, activates plan,
    and writes a credits_transaction. Kept side-effect-free until configured.
    """
    body = await request.body()
    signature = request.headers.get("stripe-signature") or request.headers.get("signature")
    try:
        result = get_payment_provider(provider).verify_webhook(body, signature)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    # TODO: on verified success -> BillingService.credit(user, plan.credits, "purchase", ref)
    return {"received": True, "provider": provider, **result}
