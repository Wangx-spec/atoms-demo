from __future__ import annotations

from app.core.config import settings
from app.services.payment.base import CheckoutSession


class StripeProvider:
    name = "stripe"

    async def create_checkout(self, plan_code: str, amount_cents: int, user_id: str) -> CheckoutSession:
        # TODO: real integration:
        #   import stripe; stripe.api_key = settings.stripe_api_key
        #   session = stripe.checkout.Session.create(...)
        if not settings.stripe_api_key:
            raise RuntimeError("STRIPE_API_KEY not configured")
        return CheckoutSession(
            provider=self.name,
            checkout_url=f"https://checkout.stripe.com/pay/stub?plan={plan_code}",
            session_id=f"cs_stub_{plan_code}_{user_id[:8]}",
        )

    def verify_webhook(self, payload: bytes, signature: str | None) -> dict:
        # TODO: stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
        return {"verified": bool(signature), "raw_size": len(payload)}
