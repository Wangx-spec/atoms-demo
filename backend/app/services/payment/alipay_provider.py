from __future__ import annotations

from app.core.config import settings
from app.services.payment.base import CheckoutSession


class AlipayProvider:
    name = "alipay"

    async def create_checkout(self, plan_code: str, amount_cents: int, user_id: str) -> CheckoutSession:
        # TODO: alipay.trade.page.pay; sign with RSA2 private key, return pay URL.
        if not settings.alipay_app_id:
            raise RuntimeError("ALIPAY_APP_ID not configured")
        return CheckoutSession(
            provider=self.name,
            checkout_url=f"https://openapi.alipay.com/gateway.do/stub?plan={plan_code}",
            session_id=f"alipay_stub_{plan_code}_{user_id[:8]}",
        )

    def verify_webhook(self, payload: bytes, signature: str | None) -> dict:
        # TODO: verify Alipay async notify signature with Alipay public key.
        return {"verified": bool(signature), "raw_size": len(payload)}


def get_payment_provider(name: str):
    from app.services.payment.stripe_provider import StripeProvider
    from app.services.payment.wechat_provider import WechatProvider

    providers = {
        "stripe": StripeProvider(),
        "wechat": WechatProvider(),
        "alipay": AlipayProvider(),
    }
    if name not in providers:
        raise ValueError(f"Unknown payment provider: {name}")
    return providers[name]
