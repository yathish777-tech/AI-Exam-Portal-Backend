"""
app/main.py
===========
FastAPI application entry point.

Startup order (important for correct initialization):
1. Logging is configured first so all subsequent startup logs are captured.
2. FastAPI app is created with lifespan context.
3. Middleware is added (order matters — outermost middleware runs first).
4. CORS is configured with explicit allowed origins (never wildcard).
5. Exception handlers are registered.
6. Routers are included.

CORS SECURITY:
- `allow_origins` is set to the exact FRONTEND_URL from configuration.
- `allow_credentials=True` requires an explicit, non-wildcard origin.
  Using `allow_origins=["*"]` with `allow_credentials=True` is rejected
  by browsers and would be a critical misconfiguration.
- `allow_methods` and `allow_headers` are restricted to necessary values.

MIDDLEWARE EXECUTION ORDER (Starlette/FastAPI):
Middleware is executed in reverse registration order for requests (last
added = first to run). Register in this order so RequestID runs FIRST:
  1. Add RequestIDMiddleware last (runs first on request)
  2. Add SecurityHeadersMiddleware
  3. Add RequestLoggingMiddleware (logs after ID is set)
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import limiter
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

settings = get_settings()


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application startup and shutdown logic.

    Startup:
    - Configure logging.
    - (Future) Warm database connection pool.
    - (Future) Load AI models.

    Shutdown:
    - (Future) Drain connection pool.
    """
    # 1. Configure logging first
    setup_logging()

    from loguru import logger
    logger.info(
        "LocalSM AI Exam Portal starting",
        environment=settings.environment,
        debug=settings.debug,
    )

    yield

    logger.info("LocalSM AI Exam Portal shutting down")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Using a factory function makes the app testable — tests can call
    create_app() with different settings overrides.
    """
    app = FastAPI(
        title="LocalSM AI Exam Portal API",
        description=(
            "Secure REST API for the LocalSM AI-powered examination platform. "
            "Authentication and session management endpoints."
        ),
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,      # Disable in production
        redoc_url="/redoc" if settings.debug else None,    # Disable in production
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # -----------------------------------------------------------------------
    # Rate limiter state
    # -----------------------------------------------------------------------
    app.state.limiter = limiter

    # -----------------------------------------------------------------------
    # Exception handlers
    # -----------------------------------------------------------------------
    register_exception_handlers(app)

    # Register slowapi rate-limit-exceeded handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # -----------------------------------------------------------------------
    # CORS
    # -----------------------------------------------------------------------
    # NEVER use allow_origins=["*"] with allow_credentials=True.
    # Allowed origins come from environment configuration.
    # -----------------------------------------------------------------------
    allowed_origins = [settings.frontend_url]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "Accept",
        ],
        expose_headers=["X-Request-ID"],
        max_age=600,  # Preflight cache: 10 minutes
    )

    # -----------------------------------------------------------------------
    # Middleware
    # Note: Last added = first executed (Starlette LIFO order).
    # -----------------------------------------------------------------------
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)   # ← Runs FIRST (outermost)

    # -----------------------------------------------------------------------
    # Routers
    # -----------------------------------------------------------------------
    app.include_router(api_v1_router)

    # -----------------------------------------------------------------------
    # Health check (always available)
    # -----------------------------------------------------------------------
    @app.get("/health", tags=["Health"], include_in_schema=settings.debug)
    async def health_check() -> dict:
        """Basic liveness probe — no sensitive data."""
        return {"status": "ok", "version": "0.1.0"}

    return app


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------
app = create_app()
