"""Rate limiting via slowapi (optional, enabled when slowapi is installed).

Usage in main.py:
    from app.core.rate_limit import setup_rate_limiting
    setup_rate_limiting(app)

And on routes:
    from app.core.rate_limit import limiter
    @router.post("...")
    @limiter.limit(settings.rate_limit_generate)
    async def handler(request: Request, ...): ...
"""
from __future__ import annotations

from app.core.config import settings

try:
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit_default])
    _AVAILABLE = True
except ImportError:  # pragma: no cover
    limiter = None
    RateLimitExceeded = None  # type: ignore
    _AVAILABLE = False


def setup_rate_limiting(app) -> None:
    if not _AVAILABLE or limiter is None:
        return
    from slowapi import _rate_limit_exceeded_handler

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
