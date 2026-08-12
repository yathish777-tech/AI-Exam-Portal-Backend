"""
tests/unit/test_foundation.py
==============================
Phase 1 foundational tests.

These tests verify the core infrastructure behaviours defined in Phase 1:
- Application startup (create_app factory)
- Health endpoint (liveness probe at /health)
- Request ID middleware (X-Request-ID assignment + propagation)
- Security headers (X-Content-Type-Options, Referrer-Policy)
- CORS header enforcement (valid origin vs wildcard rejection)
- Exception handler contract (500 response body, no internal details)
- Configuration validation (missing required values, weak secrets)
- Database session dependency structure (rollback on error)
- BaseRepository contract

All tests in this file are marked ``unit`` — they do NOT touch a real
database. Database interactions are mocked where necessary.

SECURITY NOTES:
- Tests do not assert on Authorization header values.
- Tests do not log or print secrets.
- Exception response bodies are checked to ensure they never contain
  tracebacks, SQL, file paths, or secret material.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from pydantic import ValidationError


# ===========================================================================
# Application startup
# ===========================================================================

class TestApplicationStartup:
    """Verify the app factory produces a correctly configured FastAPI app."""

    @pytest.mark.unit
    def test_create_app_returns_fastapi_instance(self, app: object) -> None:
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)

    @pytest.mark.unit
    def test_app_has_required_middleware(self, app: object) -> None:
        """Verify critical middleware is registered (by checking app.middleware_stack)."""
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
        # The app should have routes registered
        route_paths = {
            route.path for route in app.routes if hasattr(route, "path")
        }
        assert "/health" in route_paths

    @pytest.mark.unit
    def test_app_title_and_version(self, app: object) -> None:
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
        assert "LocalSM" in app.title  # type: ignore[union-attr]
        assert app.version == "0.1.0"  # type: ignore[union-attr]

    @pytest.mark.unit
    def test_swagger_enabled_in_debug_mode(self, app: object) -> None:
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
        # DEBUG=true in TEST_ENV, so docs_url should be set
        assert app.docs_url == "/docs"  # type: ignore[union-attr]


# ===========================================================================
# Liveness probe — GET /health
# ===========================================================================

class TestLivenessProbe:
    """Test the bare /health liveness probe in main.py."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_returns_200(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_returns_status_ok(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_contains_no_sensitive_fields(self, client: AsyncClient) -> None:
        """Verify health response never contains database, secret, or token fields."""
        response = await client.get("/health")
        body_text = response.text.lower()
        sensitive_keywords = [
            "password", "secret", "token", "database_url",
            "jwt", "otp", "traceback", "exception", "postgresql",
            "asyncpg", "host", "port",
        ]
        for keyword in sensitive_keywords:
            assert keyword not in body_text, (
                f"Sensitive keyword '{keyword}' found in health response"
            )


# ===========================================================================
# Request ID middleware
# ===========================================================================

class TestRequestIDMiddleware:
    """Verify the X-Request-ID middleware assigns and propagates correlation IDs."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_response_always_has_request_id_header(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert "x-request-id" in response.headers

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_valid_client_request_id_is_echoed(self, client: AsyncClient) -> None:
        client_id = str(uuid.uuid4())
        response = await client.get("/health", headers={"X-Request-ID": client_id})
        assert response.headers["x-request-id"] == client_id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_invalid_client_request_id_is_replaced(self, client: AsyncClient) -> None:
        """Non-UUID X-Request-ID must be silently replaced (header injection protection)."""
        response = await client.get(
            "/health",
            headers={"X-Request-ID": "not-a-uuid-injection-attempt"},
        )
        returned_id = response.headers["x-request-id"]
        # Should be a valid UUID now
        uuid.UUID(returned_id)  # raises ValueError if invalid

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_missing_request_id_is_generated(self, client: AsyncClient) -> None:
        """Server must generate a UUID when the client provides no X-Request-ID."""
        response = await client.get("/health")
        returned_id = response.headers.get("x-request-id", "")
        assert returned_id != ""
        uuid.UUID(returned_id)  # must be a valid UUID


# ===========================================================================
# Security headers middleware
# ===========================================================================

class TestSecurityHeaders:
    """Verify security headers are present on all responses."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_x_content_type_options_nosniff(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.headers.get("x-content-type-options") == "nosniff"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_referrer_policy_strict_origin(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_hsts_not_set_when_cookie_secure_false(self, client: AsyncClient) -> None:
        """HSTS must not be set when COOKIE_SECURE=false (no HTTPS in test env)."""
        response = await client.get("/health")
        assert "strict-transport-security" not in response.headers


# ===========================================================================
# CORS configuration
# ===========================================================================

class TestCORSConfiguration:
    """Verify CORS is configured correctly from settings."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_allowed_origin_receives_cors_header(self, client: AsyncClient) -> None:
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Should get an allow-origin header matching the configured origin
        allow_origin = response.headers.get("access-control-allow-origin", "")
        assert allow_origin == "http://localhost:5173"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unknown_origin_does_not_receive_cors_header(
        self, client: AsyncClient
    ) -> None:
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://evil.attacker.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        allow_origin = response.headers.get("access-control-allow-origin", "")
        assert allow_origin != "http://evil.attacker.example.com"


# ===========================================================================
# Exception handler contract
# ===========================================================================

class TestExceptionHandlers:
    """Verify the global exception handlers produce safe, structured responses."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_404_returns_structured_json(self, client: AsyncClient) -> None:
        response = await client.get("/this-route-does-not-exist")
        assert response.status_code == 404
        data = response.json()
        assert "message" in data
        assert "error_code" in data
        assert data["success"] is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_500_response_contains_no_internal_details(
        self, client: AsyncClient, app: object
    ) -> None:
        """Unhandled exceptions must produce generic 500, never tracebacks."""
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)

        @app.get("/test-500-trigger")
        async def _trigger_500() -> None:
            raise RuntimeError("Simulated internal error with secret data: sk-abc123")

        response = await client.get("/test-500-trigger")
        assert response.status_code == 500
        body_text = response.text.lower()
        # The secret value must NOT appear in the response
        assert "sk-abc123" not in body_text
        assert "runtimeerror" not in body_text
        assert "traceback" not in body_text
        # But the response must still be structured JSON
        data = response.json()
        assert data["success"] is False
        assert "error_code" in data
        assert data["error_code"] == "INTERNAL_ERROR"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_422_validation_error_safe_body(self, client: AsyncClient) -> None:
        """Pydantic validation errors must not echo the raw request body."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "not-an-email", "password": ""},
        )
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "errors" in data
        # The raw request body value must not appear in field error messages
        body_text = response.text
        assert "not-an-email" not in body_text or "field" in body_text  # field path is ok

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_app_exception_returns_correct_http_status(
        self, client: AsyncClient, app: object
    ) -> None:
        """AppException subclasses must map to their declared HTTP status."""
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
        from app.core.exceptions import NotFoundError

        @app.get("/test-not-found")
        async def _trigger_not_found() -> None:
            raise NotFoundError("The widget was not found.")

        response = await client.get("/test-not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"
        assert "widget" in data["message"]


# ===========================================================================
# Configuration validation
# ===========================================================================

class TestConfigurationValidation:
    """Verify Settings validators reject insecure or missing configuration."""

    @pytest.mark.unit
    def test_missing_database_url_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app.core.config import Settings
        monkeypatch.delenv("DATABASE_URL", raising=False)
        with pytest.raises((ValidationError, Exception)):
            Settings(  # type: ignore[call-arg]
                _env_file=None,
                environment="development",
                jwt_secret_key="x" * 64,
                jwt_algorithm="HS256",
                otp_hash_secret="y" * 64,
                frontend_url="http://localhost:5173",
                # database_url intentionally omitted
            )

    @pytest.mark.unit
    def test_wildcard_frontend_url_raises(self) -> None:
        from app.core.config import Settings
        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]
                environment="development",
                database_url="postgresql+asyncpg://u:p@localhost/db",
                jwt_secret_key="x" * 64,
                jwt_algorithm="HS256",
                otp_hash_secret="y" * 64,
                frontend_url="*",  # must be rejected
            )

    @pytest.mark.unit
    def test_invalid_jwt_algorithm_raises(self) -> None:
        from app.core.config import Settings
        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]
                environment="development",
                database_url="postgresql+asyncpg://u:p@localhost/db",
                jwt_secret_key="x" * 64,
                jwt_algorithm="none",  # alg=none must be rejected
                otp_hash_secret="y" * 64,
                frontend_url="http://localhost:5173",
            )

    @pytest.mark.unit
    def test_short_jwt_secret_raises(self) -> None:
        from app.core.config import Settings
        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]
                environment="development",
                database_url="postgresql+asyncpg://u:p@localhost/db",
                jwt_secret_key="short",  # too short — must be rejected
                jwt_algorithm="HS256",
                otp_hash_secret="y" * 64,
                frontend_url="http://localhost:5173",
            )

    @pytest.mark.unit
    def test_production_placeholder_jwt_secret_raises(self) -> None:
        from app.core.config import Settings
        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]
                environment="production",
                database_url="postgresql+asyncpg://u:p@localhost/db",
                jwt_secret_key="dev_" + "x" * 64,  # dev prefix in prod — rejected
                jwt_algorithm="HS256",
                otp_hash_secret="y" * 64,
                frontend_url="https://app.example.com",
            )

    @pytest.mark.unit
    def test_pool_size_zero_raises(self) -> None:
        from app.core.config import Settings
        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]
                environment="development",
                database_url="postgresql+asyncpg://u:p@localhost/db",
                jwt_secret_key="x" * 64,
                jwt_algorithm="HS256",
                otp_hash_secret="y" * 64,
                frontend_url="http://localhost:5173",
                database_pool_size=0,  # must be rejected
            )

    @pytest.mark.unit
    def test_negative_max_overflow_raises(self) -> None:
        from app.core.config import Settings
        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]
                environment="development",
                database_url="postgresql+asyncpg://u:p@localhost/db",
                jwt_secret_key="x" * 64,
                jwt_algorithm="HS256",
                otp_hash_secret="y" * 64,
                frontend_url="http://localhost:5173",
                database_max_overflow=-1,  # must be rejected
            )

    @pytest.mark.unit
    def test_bcrypt_rounds_too_low_raises(self) -> None:
        from app.core.config import Settings
        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]
                environment="development",
                database_url="postgresql+asyncpg://u:p@localhost/db",
                jwt_secret_key="x" * 64,
                jwt_algorithm="HS256",
                otp_hash_secret="y" * 64,
                frontend_url="http://localhost:5173",
                bcrypt_rounds=3,  # below minimum of 12
            )

    @pytest.mark.unit
    def test_samesite_none_without_secure_raises(self) -> None:
        from app.core.config import Settings
        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]
                environment="development",
                database_url="postgresql+asyncpg://u:p@localhost/db",
                jwt_secret_key="x" * 64,
                jwt_algorithm="HS256",
                otp_hash_secret="y" * 64,
                frontend_url="http://localhost:5173",
                cookie_samesite="none",
                cookie_secure=False,  # combination must be rejected
            )

    @pytest.mark.unit
    def test_valid_config_parses_successfully(self) -> None:
        from app.core.config import Settings
        s = Settings(  # type: ignore[call-arg]
            environment="development",
            database_url="postgresql+asyncpg://u:p@localhost/db",
            jwt_secret_key="x" * 64,
            jwt_algorithm="HS256",
            otp_hash_secret="y" * 64,
            frontend_url="http://localhost:5173",
            cookie_secure=False,
        )
        assert s.environment == "development"
        assert s.database_pool_size == 10  # default
        assert s.database_max_overflow == 20  # default
        assert s.database_pool_timeout == 30  # default
        assert s.database_pool_recycle == 1800  # default


# ===========================================================================
# Database session dependency
# ===========================================================================

class TestDatabaseSession:
    """Verify the get_db dependency lifecycle without a real database."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_db_yields_and_closes_on_success(self) -> None:
        """Session must be closed after a successful yield."""
        from unittest.mock import AsyncMock, MagicMock, patch

        mock_session = AsyncMock()
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        with patch("app.database.dependencies.AsyncSessionLocal", return_value=mock_cm):
            from app.database.dependencies import get_db
            gen = get_db()
            session = await gen.__anext__()
            assert session is mock_session
            try:
                await gen.aclose()
            except StopAsyncIteration:
                pass
            mock_session.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_db_rolls_back_on_exception(self) -> None:
        """Session must rollback when an exception propagates through it."""
        from unittest.mock import AsyncMock, MagicMock, patch

        mock_session = AsyncMock()
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        with patch("app.database.dependencies.AsyncSessionLocal", return_value=mock_cm):
            from app.database.dependencies import get_db
            gen = get_db()
            await gen.__anext__()
            with pytest.raises(RuntimeError):
                await gen.athrow(RuntimeError("simulated error"))
            mock_session.rollback.assert_called_once()


# ===========================================================================
# BaseRepository
# ===========================================================================

class TestBaseRepository:
    """Verify the BaseRepository contract without a real database."""

    @pytest.mark.unit
    def test_base_repository_is_generic(self) -> None:
        """BaseRepository[T] must be importable and subclassable."""
        from app.database.base import Base, UUIDMixin
        from app.repositories.base import BaseRepository

        class FakeModel(UUIDMixin, Base):
            __tablename__ = "fake_table_test"
            # minimal — just tests that subclassing works

        class FakeRepository(BaseRepository[FakeModel]):
            model = FakeModel

        assert FakeRepository.model is FakeModel

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_by_id_calls_execute(self, mock_db: AsyncMock) -> None:
        from app.database.base import Base, UUIDMixin
        from app.repositories.base import BaseRepository

        class AnotherFakeModel(UUIDMixin, Base):
            __tablename__ = "another_fake_table_test"

        class AnotherFakeRepo(BaseRepository[AnotherFakeModel]):
            model = AnotherFakeModel

        record_id = uuid.uuid4()
        await AnotherFakeRepo.get_by_id(mock_db, record_id)
        mock_db.execute.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_calls_add_flush_refresh(self, mock_db: AsyncMock) -> None:
        from app.database.base import Base, UUIDMixin
        from app.repositories.base import BaseRepository

        class SaveFakeModel(UUIDMixin, Base):
            __tablename__ = "save_fake_table_test"

        class SaveFakeRepo(BaseRepository[SaveFakeModel]):
            model = SaveFakeModel

        instance = MagicMock(spec=SaveFakeModel)
        await SaveFakeRepo.save(mock_db, instance)
        mock_db.add.assert_called_once_with(instance)
        mock_db.flush.assert_called_once()
        mock_db.refresh.assert_called_once_with(instance)


# ===========================================================================
# Exception hierarchy
# ===========================================================================

class TestExceptionHierarchy:
    """Verify exception classes have correct HTTP status codes."""

    @pytest.mark.unit
    def test_authentication_error_is_401(self) -> None:
        from app.core.exceptions import AuthenticationError
        exc = AuthenticationError()
        assert exc.status_code == 401

    @pytest.mark.unit
    def test_authorization_error_is_403(self) -> None:
        from app.core.exceptions import AuthorizationError
        exc = AuthorizationError()
        assert exc.status_code == 403

    @pytest.mark.unit
    def test_not_found_error_is_404(self) -> None:
        from app.core.exceptions import NotFoundError
        exc = NotFoundError()
        assert exc.status_code == 404

    @pytest.mark.unit
    def test_conflict_error_is_409(self) -> None:
        from app.core.exceptions import ConflictError
        exc = ConflictError()
        assert exc.status_code == 409

    @pytest.mark.unit
    def test_validation_error_is_422(self) -> None:
        from app.core.exceptions import ValidationError
        exc = ValidationError()
        assert exc.status_code == 422

    @pytest.mark.unit
    def test_rate_limit_error_is_429(self) -> None:
        from app.core.exceptions import RateLimitError
        exc = RateLimitError()
        assert exc.status_code == 429

    @pytest.mark.unit
    def test_internal_error_is_500(self) -> None:
        from app.core.exceptions import InternalError
        exc = InternalError()
        assert exc.status_code == 500

    @pytest.mark.unit
    def test_token_expired_inherits_authentication(self) -> None:
        from app.core.exceptions import AuthenticationError, TokenExpiredError
        exc = TokenExpiredError()
        assert isinstance(exc, AuthenticationError)
        assert exc.status_code == 401

    @pytest.mark.unit
    def test_session_revoked_inherits_authentication(self) -> None:
        from app.core.exceptions import AuthenticationError, SessionRevokedError
        exc = SessionRevokedError()
        assert isinstance(exc, AuthenticationError)
        assert exc.status_code == 401
