"""
app/middleware/rate_limit.py
============================
Per-endpoint rate limiting using slowapi (built on limits library).

SECURITY:
- Rate limits are configured via environment variables (never hard-coded).
- Limits are applied per-IP by default. For login, an additional
  per-email limit can be applied at the service layer if needed.
- The rate limiter uses in-memory storage by default. For multi-instance
  deployments, configure a shared Redis backend.
- On limit exceeded, a 429 response is returned with a generic message.

DEPLOYMENT NOTE:
  In production with multiple application instances, replace the default
  in-memory backend with a shared Redis backend:

  from limits.storage import RedisStorage
  limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379/0")

Configuration:
  RATE_LIMIT_LOGIN=5/minute
  RATE_LIMIT_SIGNUP=5/minute
  RATE_LIMIT_FORGOT_PASSWORD=3/minute
  RATE_LIMIT_VERIFY_OTP=5/minute
  RATE_LIMIT_RESET_PASSWORD=5/minute
  RATE_LIMIT_REFRESH=10/minute
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Limiter instance
# ---------------------------------------------------------------------------
# `key_func=get_remote_address` limits by client IP.
# In production behind a trusted reverse proxy, ensure X-Forwarded-For
# is set correctly by your proxy and that only the proxy's IP range
# is trusted (otherwise clients can spoof the IP).
# ---------------------------------------------------------------------------
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # No default — each endpoint declares its own limit
)
