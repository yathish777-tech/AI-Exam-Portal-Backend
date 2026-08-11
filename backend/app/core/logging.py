"""
app/core/logging.py
===================
Loguru-based structured logging configuration.

SECURITY CONTRACT — this module MUST never log:
  - Passwords (plaintext or hash)
  - JWT access tokens
  - Refresh tokens (raw or hash)
  - OTP values (raw or hash)
  - Authorization / Cookie headers
  - Database connection strings
  - Any secret key material

Log security-relevant events using `log_security_event()`.
Always include a correlation_id (request ID) for traceability.
"""

from __future__ import annotations

import sys
from typing import Any

from loguru import logger

from app.core.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def setup_logging() -> None:
    """
    Configure Loguru sinks.

    Call this once at application startup (in app/main.py lifespan).
    After calling this function, `from loguru import logger` works
    application-wide with the configured format and level.
    """
    # Remove the default Loguru handler to avoid duplicate output
    logger.remove()

    log_level = settings.log_level.upper()

    if settings.log_format == "json":
        _add_json_sink(log_level)
    else:
        _add_text_sink(log_level)

    if settings.log_file_path:
        _add_file_sink(log_level)


def _add_json_sink(level: str) -> None:
    """Add a structured JSON sink to stdout (recommended for production)."""
    logger.add(
        sys.stdout,
        level=level,
        serialize=True,               # Loguru JSON serialization
        enqueue=True,                 # thread-safe async logging
        backtrace=False,              # never expose stack traces to log sinks
        diagnose=False,               # no variable values in tracebacks
    )


def _add_text_sink(level: str) -> None:
    """Add a human-readable text sink to stdout (for local development)."""
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "{message} | {extra}"
    )
    logger.add(
        sys.stdout,
        level=level,
        format=fmt,
        colorize=True,
        enqueue=True,
        backtrace=settings.debug,     # only in debug mode
        diagnose=settings.debug,      # only in debug mode
    )


def _add_file_sink(level: str) -> None:
    """Add a rotating file sink for persistent log storage."""
    logger.add(
        settings.log_file_path,
        level=level,
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        serialize=True,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )


# ---------------------------------------------------------------------------
# Context-bound logger factory
# ---------------------------------------------------------------------------

def get_request_logger(
    request_id: str = "",
    user_id: str = "",
    endpoint: str = "",
) -> Any:
    """
    Return a Loguru logger bound with request-scoped context.

    The bound context fields appear in every log record emitted through
    this logger instance, enabling log correlation by request_id.

    Args:
        request_id: Correlation ID from X-Request-ID header.
        user_id: UUID of the authenticated user (empty string if anonymous).
        endpoint: The request path/route (for filtering in SIEM).

    Returns:
        A bound Loguru logger.
    """
    return logger.bind(
        request_id=request_id,
        user_id=user_id,
        endpoint=endpoint,
    )


# ---------------------------------------------------------------------------
# Security event logging
# ---------------------------------------------------------------------------

def log_security_event(
    event: str,
    *,
    request_id: str = "",
    user_id: str = "",
    ip_address: str = "",
    endpoint: str = "",
    success: bool = True,
    detail: str = "",
    extra: dict | None = None,
) -> None:
    """
    Emit a structured log record for a security-relevant event.

    SECURITY CONTRACT:
      - `detail` must NEVER contain passwords, tokens, OTPs, or secrets.
      - `extra` must NEVER contain sensitive values — check before passing.
      - `ip_address` is included for forensics but handle carefully in
        jurisdictions with strict PII laws.

    Args:
        event: A SecurityEvent constant (e.g. SecurityEvent.LOGIN_SUCCESS).
        request_id: Correlation ID from the request.
        user_id: UUID of the user involved (empty if not authenticated).
        ip_address: Client IP address.
        endpoint: Request path.
        success: Whether the event represents a successful action.
        detail: Short human-readable context (no secrets).
        extra: Additional structured fields (no secrets).
    """
    bound = logger.bind(
        security_event=event,
        request_id=request_id,
        user_id=user_id,
        ip_address=ip_address,
        endpoint=endpoint,
        success=success,
        **(extra or {}),
    )

    if success:
        bound.info(f"[SECURITY] {event}" + (f": {detail}" if detail else ""))
    else:
        bound.warning(f"[SECURITY] {event}" + (f": {detail}" if detail else ""))
