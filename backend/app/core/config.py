"""
app/core/config.py
==================
Application configuration via pydantic-settings.

All values are read from environment variables (or a .env file in development).
No secrets are hard-coded.

SECURITY NOTES:
- DATABASE_URL and JWT_SECRET_KEY are loaded as SecretStr to prevent
  accidental logging of their values via repr() / str().
- Calling get_settings().database_url returns the plain string needed
  by SQLAlchemy. Avoid logging this value.
- The FRONTEND_URL validator rejects wildcard origins.
- This module validates JWT_ALGORITHM against an allowlist on startup.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import (
    SecretStr,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    Field defaults represent secure production-oriented values.
    Override them via environment variables or the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # silently ignore unknown env vars
    )

    # -----------------------------------------------------------------------
    # Application
    # -----------------------------------------------------------------------
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # -----------------------------------------------------------------------
    # Database
    # -----------------------------------------------------------------------
    # SecretStr prevents the connection string (including password) from
    # appearing in repr() / log output.
    database_url: SecretStr

    @property
    def database_url_str(self) -> str:
        """Plain string for SQLAlchemy engine creation."""
        return self.database_url.get_secret_value()

    # -----------------------------------------------------------------------
    # Database Connection Pool
    # -----------------------------------------------------------------------
    # These mirror SQLAlchemy's create_async_engine pool kwargs.
    # Defaults match the previous hard-coded values — no behaviour change
    # unless explicitly overridden via environment variables.
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 1800  # 30 minutes

    # -----------------------------------------------------------------------
    # JWT
    # -----------------------------------------------------------------------
    jwt_secret_key: SecretStr | None = None
    jwt_private_key: SecretStr | None = None
    jwt_public_key: SecretStr | None = None
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = ""   # empty = skip iss validation
    jwt_audience: str = "" # empty = skip aud validation

    # -----------------------------------------------------------------------
    # Token Expiry
    # -----------------------------------------------------------------------
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # -----------------------------------------------------------------------
    # Password Hashing
    # -----------------------------------------------------------------------
    bcrypt_rounds: int = 12

    # -----------------------------------------------------------------------
    # OTP
    # -----------------------------------------------------------------------
    otp_expire_minutes: int = 10
    otp_max_attempts: int = 5
    otp_hash_secret: SecretStr

    # -----------------------------------------------------------------------
    # CORS / Frontend
    # -----------------------------------------------------------------------
    frontend_url: str

    # -----------------------------------------------------------------------
    # Cookie
    # -----------------------------------------------------------------------
    cookie_secure: bool = True
    cookie_samesite: Literal["strict", "lax", "none"] = "lax"
    cookie_domain: str = ""  # empty = use request domain (browser default)

    # -----------------------------------------------------------------------
    # Rate Limiting
    # -----------------------------------------------------------------------
    rate_limit_login: str = "5/minute"
    rate_limit_signup: str = "5/minute"
    rate_limit_forgot_password: str = "3/minute"
    rate_limit_verify_otp: str = "5/minute"
    rate_limit_reset_password: str = "5/minute"
    rate_limit_refresh: str = "10/minute"

    # -----------------------------------------------------------------------
    # Logging
    # -----------------------------------------------------------------------
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"
    log_file_path: str = ""  # empty = stdout only

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, v: str) -> str:
        """
        Restrict JWT algorithms to a known-safe allowlist.
        'none' must NEVER be accepted — it disables signature verification.
        """
        allowed = {"HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256"}
        if v not in allowed:
            raise ValueError(
                f"JWT algorithm '{v}' is not in the allowed list: {allowed}. "
                "Do not use 'none' — it disables signature verification."
            )
        return v

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug_env(cls, v: object) -> object:
        """
        Accept common non-boolean DEBUG values from the host environment.

        Some systems set DEBUG=release or DEBUG=debug globally; without this,
        that ambient value can override the project's .env and break startup.
        """
        if isinstance(v, str):
            normalized = v.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"debug", "dev", "development"}:
                return True
        return v

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, v: SecretStr | None) -> SecretStr | None:
        """Enforce a minimum key length (64 hex chars = 256 bits)."""
        if v is None:
            return v
        raw = v.get_secret_value()
        if len(raw) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(64))\""
            )
        return v

    @field_validator("otp_hash_secret")
    @classmethod
    def validate_otp_hash_secret(cls, v: SecretStr) -> SecretStr:
        """Require an independent server-side secret for OTP HMAC digests."""
        raw = v.get_secret_value()
        if len(raw) < 32:
            raise ValueError(
                "OTP_HASH_SECRET must be at least 32 characters. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v

    @field_validator("frontend_url")
    @classmethod
    def validate_frontend_url(cls, v: str) -> str:
        """Reject wildcard or empty CORS origins."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("FRONTEND_URL must not be empty.")
        if stripped in ("*", "null"):
            raise ValueError(
                "FRONTEND_URL must not be a wildcard ('*') or 'null'. "
                "Set it to the exact frontend origin, e.g. https://example.com"
            )
        return stripped

    @field_validator("bcrypt_rounds")
    @classmethod
    def validate_bcrypt_rounds(cls, v: int) -> int:
        """
        Prevent accidental use of an insecurely low cost factor.
        12 is the recommended minimum for 2024+ hardware.
        """
        if v < 12:
            raise ValueError(
                f"BCRYPT_ROUNDS={v} is dangerously low. "
                "Minimum recommended value is 12."
            )
        if v > 20:
            raise ValueError(
                f"BCRYPT_ROUNDS={v} is impractically high and will cause "
                "severe request latency."
            )
        return v

    @field_validator("database_pool_size")
    @classmethod
    def validate_pool_size(cls, v: int) -> int:
        """Prevent pool sizes that would exhaust or under-use the DB."""
        if v < 1:
            raise ValueError("DATABASE_POOL_SIZE must be at least 1.")
        if v > 100:
            raise ValueError(
                f"DATABASE_POOL_SIZE={v} is unusually large. "
                "Verify this is intentional."
            )
        return v

    @field_validator("database_max_overflow")
    @classmethod
    def validate_max_overflow(cls, v: int) -> int:
        """Reject negative overflow values."""
        if v < 0:
            raise ValueError("DATABASE_MAX_OVERFLOW must be >= 0.")
        return v

    @model_validator(mode="after")
    def validate_cookie_samesite_with_secure(self) -> "Settings":
        """
        SameSite=None requires Secure=True (browser requirement).
        Warn/reject unsafe combinations at startup.
        """
        if self.cookie_samesite == "none" and not self.cookie_secure:
            raise ValueError(
                "COOKIE_SAMESITE=none requires COOKIE_SECURE=true. "
                "Browsers reject SameSite=None cookies without the Secure flag."
            )
        return self

    @model_validator(mode="after")
    def validate_jwt_key_material(self) -> "Settings":
        """Ensure configured JWT algorithm has matching server-side key material."""
        if self.jwt_algorithm.startswith("HS"):
            if self.jwt_secret_key is None:
                raise ValueError("JWT_SECRET_KEY is required for HS* JWT algorithms.")
            raw_secret = self.jwt_secret_key.get_secret_value()
            insecure_placeholders = {
                "secret",
                "password",
                "1234",
                "development-secret",
                "dev-secret",
                "change-me",
                "changeme",
            }
            if self.environment == "production" and (
                raw_secret.lower() in insecure_placeholders
                or raw_secret.lower().startswith("dev_")
            ):
                raise ValueError(
                    "JWT_SECRET_KEY must be a strong production secret, not a "
                    "development placeholder."
                )
            return self

        if (
            self.jwt_private_key is None
            or self.jwt_public_key is None
            or not self.jwt_private_key.get_secret_value().strip()
            or not self.jwt_public_key.get_secret_value().strip()
        ):
            raise ValueError(
                "JWT_PRIVATE_KEY and JWT_PUBLIC_KEY are required for asymmetric "
                "JWT algorithms."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Using lru_cache means the Settings object (and .env file) is parsed
    exactly once per process. Call get_settings.cache_clear() in tests
    to reload settings between test cases.
    """
    return Settings()  # type: ignore[call-arg]
