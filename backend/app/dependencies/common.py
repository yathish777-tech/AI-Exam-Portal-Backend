"""
app/dependencies/common.py
===========================
Shared FastAPI dependencies used across multiple endpoints.
"""

from __future__ import annotations

from fastapi import Request

from app.core.constants import REQUEST_ID_HEADER


def get_request_id(request: Request) -> str:
    """
    Return the request ID from request state (set by RequestIDMiddleware).

    Falls back to an empty string if not set.
    """
    return getattr(request.state, "request_id", "")


def get_client_ip(request: Request) -> str:
    """
    Return the client IP address.

    Reads from X-Forwarded-For if behind a trusted proxy; otherwise
    uses the direct connection address.

    IMPORTANT: X-Forwarded-For can be spoofed by clients. Only trust it
    if your reverse proxy is configured to overwrite it (not append).
    Configure your proxy to set a single trusted IP.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP (leftmost = original client, if proxy is trusted)
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else ""


def get_user_agent(request: Request) -> str:
    """Return the User-Agent header value, truncated to a safe length."""
    ua = request.headers.get("User-Agent", "")
    return ua[:512]  # Truncate to prevent oversized log entries
