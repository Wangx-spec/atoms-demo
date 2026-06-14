"""Payment provider interface.

Concrete providers create a checkout session and verify webhook signatures.
These are stubs: fill in credentials (via env) and the real SDK calls when going
live. They return placeholder data so the flow can be wired end-to-end in dev.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class CheckoutSession:
    provider: str
    checkout_url: str
    session_id: str


class PaymentProvider(Protocol):
    name: str

    async def create_checkout(self, plan_code: str, amount_cents: int, user_id: str) -> CheckoutSession: ...

    def verify_webhook(self, payload: bytes, signature: str | None) -> dict: ...
