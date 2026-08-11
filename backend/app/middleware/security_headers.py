"""
app/middleware/security_headers.py
===================================
Middleware that adds security-relevant HTTP response headers.

Headers added to ALL responses:
- X-Content-Type-Options: nosniff
  Prevents MIME-type sniffing (reduces XSS attack surface).
- Referrer-Policy: strict-origin-when-cross-origin
  Limits Referer header leakage.

Headers added to /auth/* responses (sensitive endpoints):
- Cache-Control: no-store
  Prevents browsers and proxies from caching authentication responses.

Headers added when COOKIE_SECURE=true (HTTPS production):
- Strict-Transport-Security
  Instructs browsers to use HTTPS only. Only set when we can confirm
  HTTPS is in use (inferred from COOKIE_SECURE setting).

NOT included (intentionally):
- X-Frame-Options: Not relevant for a pure API (no HTML frames).
- Content-Security-Policy: CSP is configured at the frontend; applying it
  to API JSON responses has no security benefit.

NOTE: Do not blindly apply browser-specific security headers to API
responses. Only include headers that provide security value for an API.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings

settings = get_settings()

# HSTS max-age in seconds. 1 year (31536000) is the OWASP recommendation.
_HSTS_MAX_AGE = 31536000


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all API responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)

        # Always apply
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Cache-Control on auth endpoints
        if request.url.path.startswith("/api/v1/auth"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Pragma"] = "no-cache"

        # HSTS — only when running over HTTPS (inferred from COOKIE_SECURE)
        if settings.cookie_secure:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={_HSTS_MAX_AGE}; includeSubDomains"
            )

        return response
