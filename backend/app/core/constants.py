"""
app/core/constants.py
=====================
Project-wide enumerations and constants.

Keeping these in a single file prevents circular imports and ensures
a single source of truth for role names, OTP purposes, and security events.
"""

from __future__ import annotations

from enum import StrEnum


# ---------------------------------------------------------------------------
# Role Names
# ---------------------------------------------------------------------------
class RoleName(StrEnum):
    """
    Application roles.

    IMPORTANT: These must exactly match the `name` column values
    seeded into the `roles` table by Alembic. Changing these values
    requires a coordinated migration.
    """

    ADMIN = "ADMIN"
    INTERVIEWER = "INTERVIEWER"
    CANDIDATE = "CANDIDATE"


# ---------------------------------------------------------------------------
# OTP Purpose
# ---------------------------------------------------------------------------
class OTPPurpose(StrEnum):
    """Supported OTP use-cases. Extend here as new flows are added."""

    PASSWORD_RESET = "password_reset"


# ---------------------------------------------------------------------------
# Security / Audit Event Names
# ---------------------------------------------------------------------------
class SecurityEvent(StrEnum):
    """
    Canonical names for security-relevant log events.

    Use these constants everywhere instead of bare strings to ensure
    consistent, searchable log entries in your SIEM.
    """

    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGIN_INACTIVE_ACCOUNT = "LOGIN_INACTIVE_ACCOUNT"
    LOGOUT = "LOGOUT"
    LOGOUT_ALL = "LOGOUT_ALL"
    SIGNUP_SUCCESS = "SIGNUP_SUCCESS"
    SIGNUP_DUPLICATE_EMAIL = "SIGNUP_DUPLICATE_EMAIL"
    PASSWORD_RESET_REQUESTED = "PASSWORD_RESET_REQUESTED"
    PASSWORD_RESET_OTP_VERIFIED = "PASSWORD_RESET_OTP_VERIFIED"
    PASSWORD_RESET_OTP_FAILED = "PASSWORD_RESET_OTP_FAILED"
    PASSWORD_RESET_OTP_EXPIRED = "PASSWORD_RESET_OTP_EXPIRED"
    PASSWORD_RESET_OTP_MAX_ATTEMPTS = "PASSWORD_RESET_OTP_MAX_ATTEMPTS"
    PASSWORD_RESET_SUCCESS = "PASSWORD_RESET_SUCCESS"
    SESSION_CREATED = "SESSION_CREATED"
    SESSION_REVOKED = "SESSION_REVOKED"
    ALL_SESSIONS_REVOKED = "ALL_SESSIONS_REVOKED"
    REFRESH_TOKEN_ROTATION = "REFRESH_TOKEN_ROTATION"
    REFRESH_TOKEN_REUSE_DETECTED = "REFRESH_TOKEN_REUSE_DETECTED"
    REFRESH_TOKEN_INVALID = "REFRESH_TOKEN_INVALID"
    TOKEN_VALIDATION_FAILED = "TOKEN_VALIDATION_FAILED"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


# ---------------------------------------------------------------------------
# Password Policy
# ---------------------------------------------------------------------------
PASSWORD_MIN_LENGTH: int = 10
PASSWORD_MAX_LENGTH: int = 128  # Prevent bcrypt resource exhaustion (> 72 bytes)

# ---------------------------------------------------------------------------
# Token Types
# ---------------------------------------------------------------------------
ACCESS_TOKEN_TYPE: str = "access"
REFRESH_TOKEN_TYPE: str = "refresh"

# ---------------------------------------------------------------------------
# OTP
# ---------------------------------------------------------------------------
OTP_LENGTH: int = 6  # digits — 10^6 = 1,000,000 possibilities

# ---------------------------------------------------------------------------
# Request ID Header
# ---------------------------------------------------------------------------
REQUEST_ID_HEADER: str = "X-Request-ID"
