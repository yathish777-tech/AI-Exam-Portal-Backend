"""
tests/conftest.py
=================
Shared pytest fixtures for the LocalSM AI Exam Portal test suite.

Architecture:
- Settings are overridden per-test via environment variable patching so
  tests never depend on a real .env file being present.
- The FastAPI app is created fresh per test session using the factory
  function to ensure middleware is applied.
- An httpx.AsyncClient is provided for endpoint-level tests that need
  the full middleware stack (CORS, request ID, security headers, etc.).
- No real database is required for unit tests. Integration tests that
  need a real DB should override the `db` fixture and set TEST_DATABASE_URL.

Security:
- Test secrets are obviously fake values with enough entropy to pass
  all validators (min-length checks, algorithm allowlists, etc.).
- No production secrets appear here.
- get_settings.cache_clear() is called between tests that mutate settings
  to prevent test pollution.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


# ---------------------------------------------------------------------------
# Minimal valid environment for Settings — all secrets are obviously fake.
# These satisfy all validators (min lengths, allowlists, etc.).
# ---------------------------------------------------------------------------
TEST_ENV: dict[str, str] = {
    "ENVIRONMENT": "development",
    "DEBUG": "true",
    "DATABASE_URL": "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb",
    "JWT_SECRET_KEY": "x" * 64,   # 64 chars — satisfies 32-char minimum
    "JWT_ALGORITHM": "HS256",
    "OTP_HASH_SECRET": "y" * 64,  # 64 chars — satisfies 32-char minimum
    "FRONTEND_URL": "http://localhost:5173",
    "COOKIE_SECURE": "false",     # no HTTPS in tests
    "COOKIE_SAMESITE": "lax",
    "LOG_LEVEL": "WARNING",       # suppress INFO noise during tests
    "LOG_FORMAT": "text",
    "BCRYPT_ROUNDS": "12",        # minimum secure value accepted by Settings
}

# Some modules import Settings during pytest collection, before fixtures run.
# Ensure collection uses the secure test configuration instead of local .env.
os.environ.update(TEST_ENV)


@pytest.fixture(autouse=True)
def override_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Patch os.environ with TEST_ENV values before every test.

    The fixture is ``autouse=True`` so it applies to every test in the
    suite without needing to be declared explicitly. This ensures that:
    - Tests never fail because a real .env file is missing.
    - Tests never accidentally use production credentials.
    - Settings are isolated between tests that mutate them.
    """
    for key, value in TEST_ENV.items():
        monkeypatch.setenv(key, value)

    # Clear the lru_cache so each test gets a fresh Settings instance
    # built from the patched environment.
    from app.core.config import get_settings
    get_settings.cache_clear()

    yield  # type: ignore[misc]

    # After the test, clear the cache again so the next test starts clean.
    get_settings.cache_clear()


@pytest.fixture()
def test_settings() -> Any:
    """Return the Settings instance built from TEST_ENV."""
    from app.core.config import get_settings
    return get_settings()


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

@pytest.fixture()
def app() -> Any:
    """
    Create a fresh FastAPI application instance for each test.

    Uses the factory function so all middleware, CORS, and exception
    handlers are applied \u2014 the same code path as production.

    The lifespan (DB warm-up / dispose) is NOT triggered here because
    httpx.AsyncClient uses the app without invoking lifespan by default.
    Use ``async with AsyncClient(app=app, ...) as client`` with
    ``lifespan=`` only in integration tests that have a real DB.
    """
    from app.main import create_app
    return create_app()


# ---------------------------------------------------------------------------
# HTTP client
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def client(app: Any) -> AsyncGenerator[AsyncClient, None]:
    """
    Yield an httpx.AsyncClient connected to the test app.

    The client sends requests through the full middleware stack (request ID,
    security headers, CORS, rate limiter, exception handlers) without
    needing a running server or a real database.

    Usage::

        async def test_health(client: AsyncClient) -> None:
            response = await client.get("/health")
            assert response.status_code == 200
    """
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Mock database session
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_db() -> AsyncMock:
    """
    Return a mock AsyncSession for unit tests that need a DB parameter
    without executing real queries.

    The mock's execute() returns a MagicMock result with a scalar_one_or_none()
    that returns None by default. Override in individual tests as needed::

        mock_db.execute.return_value.scalar_one_or_none.return_value = some_user
    """
    session = AsyncMock()
    session.add = MagicMock()
    session.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=None),
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))),
    )
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session
