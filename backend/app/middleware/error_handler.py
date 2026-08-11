"""
app/middleware/error_handler.py
================================
Global exception handlers for FastAPI.

SECURITY PRINCIPLES:
- AppException subclasses produce structured JSON with the pre-defined
  safe message and error_code. Internal details are never exposed.
- Unhandled exceptions produce a generic 500 response. The real error
  is logged server-side with the correlation ID for tracing.
- Pydantic ValidationError produces a 422 with field-level details —
  these are safe to return (they describe schema violations, not internals).
- HTTPException from FastAPI/Starlette is passed through as-is.
- Stack traces NEVER appear in response bodies in production.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """
        Convert AppException (and all subclasses) to a structured JSON response.

        The `exc.message` is pre-screened at raise time to be safe for clients.
        """
        request_id = getattr(request.state, "request_id", "")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "error_code": exc.error_code,
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id} if request_id else {},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic v2 validation errors (schema violations).

        Field-level errors are safe to return — they describe input format
        requirements, not internal implementation details.

        NOTE: Never include `exc.body` in the response — it would echo
        back the user's raw request body, which may contain passwords.
        """
        request_id = getattr(request.state, "request_id", "")
        # Extract field errors without echoing raw values
        errors = [
            {
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", "Validation error"),
                "type": err.get("type", ""),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Request validation failed.",
                "error_code": "VALIDATION_ERROR",
                "errors": errors,
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id} if request_id else {},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle standard Starlette HTTP exceptions (404, 405, etc.)."""
        request_id = getattr(request.state, "request_id", "")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error_code": f"HTTP_{exc.status_code}",
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id} if request_id else {},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all for unexpected exceptions.

        SECURITY: Never include exc details in the response body.
        Log the full traceback server-side with the correlation ID.
        """
        request_id = getattr(request.state, "request_id", "")
        logger.opt(exception=True).error(
            f"Unhandled exception on {request.method} {request.url.path}",
            request_id=request_id,
            exc_type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "An unexpected server error occurred.",
                "error_code": "INTERNAL_ERROR",
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id} if request_id else {},
        )
