"""
app/api/v1/health.py
====================
Health check endpoint for the API v1 router.

Two probes are available:

  GET /api/v1/health
      Full readiness probe. Verifies application is running AND
      the database is reachable with a lightweight SELECT 1 query.
      Returns 200 on success, 503 if the database is unreachable.

Security:
- No database credentials, connection strings, or internal details
  are ever included in the response body.
- No authentication required (liveness/readiness probes must work
  without credentials).
- Health check does NOT appear in the Swagger schema in production
  (include_in_schema respects the debug setting).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.dependencies import get_db

settings = get_settings()

router = APIRouter(prefix="/health", tags=["Health"])

_VERSION = "0.1.0"


@router.get(
    "",
    summary="Readiness probe",
    description=(
        "Verify application and database availability. "
        "Returns 200 with status=healthy when the DB is reachable, "
        "503 with status=degraded when it is not. "
        "No sensitive information is included in the response."
    ),
    include_in_schema=settings.debug,  # hide from production Swagger
)
async def health_check(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """
    Readiness probe.

    Executes a lightweight ``SELECT 1`` to verify the database connection
    is alive. Returns HTTP 200 on success, HTTP 503 on failure.

    The response body deliberately omits any internal detail that would
    help an attacker understand the infrastructure (no host, port,
    driver version, or error message from the database layer).
    """
    try:
        await db.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "version": _VERSION,
            },
        )
    except Exception as exc:
        # Log the real error server-side with no sensitive detail in the body.
        logger.error(
            "Health check: database probe failed",
            exc_type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "version": _VERSION,
                "detail": "Database is currently unavailable.",
            },
        )
