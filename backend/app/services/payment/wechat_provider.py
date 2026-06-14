from __future__ import annotations

from app.core.config import settings
from app.services.payment.base import CheckoutSession


class WechatProvider:
    name = "wechat"

    async def create_checkout(self, plan_code: str, amount_cents: int, user_id: str) -> CheckoutSession:
        # TODO: WeChat Pay Native/JSAPI unified order; return code_url for QR display.
        if not settings.wechat_pay_key:
            raise RuntimeError("WECHAT_PAY_KEY not configured")
        return CheckoutSession(
            provider=self.name,
            checkout_url=f"weixin://wxpay/stub?plan={plan_code}",
            session_id=f"wx_stub_{plan_code}_{user_id[:8]}",
        )

    def verify_webhook(self, payload: bytes, signature: str | None) -> dict:
        # TODO: verify WeChat Pay V3 signature with platform certificate.
        return {"verified": bool(signature), "raw_size": len(payload)}
