"""
app/middleware/logging.py
=========================
HTTP request/response logging middleware.

SECURITY CONTRACT — this middleware MUST NOT log:
- Request body (may contain passwords, tokens, OTPs)
- Authorization header
- Cookie header
- Any header value that may contain credentials

Logs are structured and include:
- request_id (correlation ID from request.state)
- HTTP method and path
- Response status code
- Request duration in milliseconds
- Client IP (for forensics)
- user_id (from request.state, if authenticated)

Path normalization: query strings are excluded from logged paths
to avoid capturing sensitive query parameters.
"""

from __future__ import annotations

import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log each HTTP request with timing, status, and correlation ID."""

    # Paths to skip (e.g. health checks that flood logs)
    _SKIP_PATHS: set[str] = {"/health", "/metrics", "/favicon.ico"}

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        path = request.url.path

        if path in self._SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        request_id = getattr(request.state, "request_id", "")
        client_ip = request.client.host if request.client else ""

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        user_id = getattr(request.state, "user_id", "")
        status_code = response.status_code

        log_fn = logger.warning if status_code >= 400 else logger.info

        log_fn(
            f"{request.method} {path} → {status_code}",
            request_id=request_id,
            method=request.method,
            path=path,   # query string excluded
            status_code=status_code,
            duration_ms=duration_ms,
            ip=client_ip,
            user_id=user_id,
        )

        return response
