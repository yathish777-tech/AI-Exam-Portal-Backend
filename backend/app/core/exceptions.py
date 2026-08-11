"""
app/core/exceptions.py
======================
Application exception hierarchy.

Design principles:
- Every exception carries an `error_code` (a machine-readable constant)
  and a human-readable `message`.
- HTTP status codes are attached to exception classes, not to callers.
- The global error handler (middleware/error_handler.py) converts these
  into structured JSON responses that NEVER expose internal details.
- Raw Python exceptions, SQLAlchemy errors, and stack traces must NEVER
  reach the client response body.
"""

from __future__ import annotations

from http import HTTPStatus


class AppException(Exception):
    """
    Base class for all application-level exceptions.

    Attributes:
        message:    Human-readable description (safe for client consumption).
        error_code: Machine-readable code for client-side error handling.
        status_code: HTTP status code to return.
    """

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        error_code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if error_code is not None:
            self.error_code = error_code
        if status_code is not None:
            self.status_code = status_code


# ---------------------------------------------------------------------------
# 401 — Authentication failures
# ---------------------------------------------------------------------------

class AuthenticationError(AppException):
    """
    Raised when authentication fails for any reason.

    IMPORTANT: The public-facing message must NEVER reveal whether the
    failure was due to a wrong password vs an unknown email. Use generic
    messages to prevent user enumeration attacks.
    """

    status_code = HTTPStatus.UNAUTHORIZED.value
    error_code = "AUTHENTICATION_FAILED"

    def __init__(
        self,
        message: str = "Invalid credentials.",
        error_code: str = "AUTHENTICATION_FAILED",
    ) -> None:
        super().__init__(message=message, error_code=error_code)


class TokenExpiredError(AuthenticationError):
    """Raised when a JWT or refresh token has expired."""

    error_code = "TOKEN_EXPIRED"

    def __init__(self, message: str = "Token has expired.") -> None:
        super().__init__(message=message, error_code=self.error_code)


class TokenInvalidError(AuthenticationError):
    """Raised for malformed, tampered, or otherwise invalid tokens."""

    error_code = "TOKEN_INVALID"

    def __init__(self, message: str = "Token is invalid.") -> None:
        super().__init__(message=message, error_code=self.error_code)


class SessionRevokedError(AuthenticationError):
    """Raised when the session associated with a token has been revoked."""

    error_code = "SESSION_REVOKED"

    def __init__(self, message: str = "Session has been revoked.") -> None:
        super().__init__(message=message, error_code=self.error_code)


class AccountDisabledError(AuthenticationError):
    """Raised when an inactive account attempts to authenticate."""

    error_code = "ACCOUNT_DISABLED"

    def __init__(self, message: str = "This account has been disabled.") -> None:
        super().__init__(message=message, error_code=self.error_code)


# ---------------------------------------------------------------------------
# 403 — Authorization failures
# ---------------------------------------------------------------------------

class AuthorizationError(AppException):
    """
    Raised when an authenticated user lacks permission for an action.

    Do not reveal which specific permission was missing — return a generic
    forbidden message to prevent leaking authorization structure.
    """

    status_code = HTTPStatus.FORBIDDEN.value
    error_code = "AUTHORIZATION_FAILED"

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        error_code: str = "AUTHORIZATION_FAILED",
    ) -> None:
        super().__init__(message=message, error_code=error_code)


# ---------------------------------------------------------------------------
# 404 — Not found
# ---------------------------------------------------------------------------

class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    status_code = HTTPStatus.NOT_FOUND.value
    error_code = "NOT_FOUND"

    def __init__(
        self,
        message: str = "The requested resource was not found.",
        error_code: str = "NOT_FOUND",
    ) -> None:
        super().__init__(message=message, error_code=error_code)


# ---------------------------------------------------------------------------
# 409 — Conflict
# ---------------------------------------------------------------------------

class ConflictError(AppException):
    """Raised for resource conflicts (e.g. duplicate email on signup)."""

    status_code = HTTPStatus.CONFLICT.value
    error_code = "CONFLICT"

    def __init__(
        self,
        message: str = "A conflict occurred.",
        error_code: str = "CONFLICT",
    ) -> None:
        super().__init__(message=message, error_code=error_code)


# ---------------------------------------------------------------------------
# 422 — Validation / business rule failures
# ---------------------------------------------------------------------------

class ValidationError(AppException):
    """
    Raised when business-rule validation fails (distinct from Pydantic
    schema validation which FastAPI handles automatically).
    """

    status_code = HTTPStatus.UNPROCESSABLE_ENTITY.value
    error_code = "VALIDATION_ERROR"

    def __init__(
        self,
        message: str = "Validation failed.",
        error_code: str = "VALIDATION_ERROR",
    ) -> None:
        super().__init__(message=message, error_code=error_code)


class OTPError(AppException):
    """OTP-specific errors (invalid, expired, max attempts)."""

    status_code = HTTPStatus.UNPROCESSABLE_ENTITY.value
    error_code = "OTP_ERROR"

    def __init__(
        self,
        message: str = "OTP verification failed.",
        error_code: str = "OTP_ERROR",
    ) -> None:
        super().__init__(message=message, error_code=error_code)


# ---------------------------------------------------------------------------
# 429 — Rate limiting
# ---------------------------------------------------------------------------

class RateLimitError(AppException):
    """Raised when a client exceeds the configured rate limit."""

    status_code = HTTPStatus.TOO_MANY_REQUESTS.value
    error_code = "RATE_LIMIT_EXCEEDED"

    def __init__(
        self,
        message: str = "Too many requests. Please try again later.",
        error_code: str = "RATE_LIMIT_EXCEEDED",
    ) -> None:
        super().__init__(message=message, error_code=error_code)


# ---------------------------------------------------------------------------
# 500 — Internal
# ---------------------------------------------------------------------------

class InternalError(AppException):
    """
    Raised for unexpected server-side failures.

    The message sent to the client must be generic. Log the real cause
    server-side with the correlation ID for traceability.
    """

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str = "An unexpected server error occurred.",
        error_code: str = "INTERNAL_ERROR",
    ) -> None:
        super().__init__(message=message, error_code=error_code)
