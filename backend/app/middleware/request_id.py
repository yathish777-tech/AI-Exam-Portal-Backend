"""
app/middleware/request_id.py
=============================
Middleware that assigns a correlation ID to every request.

Behaviour:
- If the client sends a valid UUID in X-Request-ID, it is used as-is.
- If the client sends an invalid value, a new UUID is generated
  (the invalid header is silently replaced).
- If no header is present, a UUID is generated.
- The correlation ID is stored in request.state.request_id.
- The correlation ID is returned in the X-Request-ID response header.

SECURITY: We validate the incoming header as a UUID to prevent
header injection attacks via an unconstrained header value.
"""

from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.constants import REQUEST_ID_HEADER


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assign and propagate a per-request correlation ID."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Attempt to use client-provided ID; validate it is a UUID
        incoming = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = _parse_or_generate_uuid(incoming)

        # Attach to request state so handlers and logging can access it
        request.state.request_id = request_id
        # Initialise user_id state field (populated by auth dependency)
        request.state.user_id = ""

        response = await call_next(request)

        # Always return the correlation ID in the response header
        response.headers[REQUEST_ID_HEADER] = request_id

        return response


def _parse_or_generate_uuid(value: str) -> str:
    """
    Return the value if it is a valid UUID4 string; otherwise generate one.
    """
    if value:
        try:
            parsed = uuid.UUID(value, version=4)
            return str(parsed)
        except ValueError:
            pass
    return str(uuid.uuid4())
