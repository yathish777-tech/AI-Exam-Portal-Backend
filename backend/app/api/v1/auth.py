"""
app/api/v1/auth.py
==================
FastAPI router for authentication endpoints.

This layer handles HTTP concerns only:
- Request parsing (Pydantic schemas)
- Cookie management (HttpOnly, Secure, SameSite)
- Rate limiting (slowapi decorators)
- Calling the AuthService
- Building HTTP responses

Business logic lives in app/services/auth_service.py.

SECURITY NOTES:
- Refresh token is delivered as an HttpOnly; Secure; SameSite cookie.
  It is NEVER echoed in the JSON response body.
- Access token is in the JSON response body (for SPA memory storage).
- All endpoints that change state require authentication (except signup,
  login, forgot-password, verify-otp, reset-password).
- Rate limits are applied per endpoint from environment configuration.
- Cookie attributes are configurable (COOKIE_SECURE, COOKIE_SAMESITE).

Cookie design:
  POST /login  → set refresh_token cookie
  POST /refresh → read refresh_token cookie, set new one
  POST /logout  → clear refresh_token cookie
  POST /logout-all → clear refresh_token cookie
"""

from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, Request, Response
from fastapi.encoders import jsonable_encoder
from starlette.datastructures import URL
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import REQUEST_ID_HEADER
from app.database.dependencies import get_db
from app.dependencies.auth import (
    AuthenticatedUser,
    get_current_user,
    get_current_user_context,
)
from app.dependencies.common import get_client_ip, get_request_id, get_user_agent
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
    VerifyOTPRequest,
)
from app.services.auth_service import AuthService

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------------------------------------------------------
# Cookie configuration constants
# ---------------------------------------------------------------------------
_REFRESH_COOKIE_NAME = "refresh_token"
_REFRESH_COOKIE_PATH = "/api/v1/auth"  # Restrict cookie to auth routes only
_ACCESS_TOKEN_EXPIRES_SECONDS = settings.access_token_expire_minutes * 60


def _set_refresh_cookie(response: Response, raw_refresh_token: str) -> None:
    """
    Set the refresh token as an HttpOnly secure cookie.

    Cookie attributes:
    - httponly=True: Inaccessible to JavaScript (XSS protection).
    - secure=True: Only sent over HTTPS (must be True in production).
    - samesite: Configurable (default 'lax' — prevents CSRF in most cases).
    - path: Restricted to auth routes to reduce attack surface.
    - max_age: Set to refresh token expiry in seconds.
    """
    response.set_cookie(
        key=_REFRESH_COOKIE_NAME,
        value=raw_refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path=_REFRESH_COOKIE_PATH,
        max_age=settings.refresh_token_expire_days * 86400,
        domain=settings.cookie_domain or None,
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Clear the refresh token cookie on logout."""
    response.delete_cookie(
        key=_REFRESH_COOKIE_NAME,
        path=_REFRESH_COOKIE_PATH,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain or None,
    )


def _build_response(
    request: Request,
    response: Response,
    status_code: int = 200,
    content: dict | None = None,
) -> JSONResponse:
    """Build a JSONResponse with the X-Request-ID header."""
    request_id = getattr(request.state, "request_id", "")
    headers = {REQUEST_ID_HEADER: request_id}
    if hasattr(response, "headers"):
        # Propagate cookies set on the response object
        for key, value in response.headers.items():
            if key.lower() == "set-cookie":
                headers["Set-Cookie"] = value
    return JSONResponse(
        status_code=status_code,
        content=content or {},
        headers=headers,
    )


def _same_origin(candidate: str, expected_origin: str) -> bool:
    """Return True when candidate URL/header has the configured frontend origin."""
    try:
        parsed = URL(candidate)
        expected = URL(expected_origin)
    except Exception:
        return False
    return (
        parsed.scheme == expected.scheme
        and parsed.hostname == expected.hostname
        and (parsed.port or _default_port(parsed.scheme))
        == (expected.port or _default_port(expected.scheme))
    )


def _default_port(scheme: str) -> int | None:
    if scheme == "http":
        return 80
    if scheme == "https":
        return 443
    return None


def _validate_cookie_csrf(request: Request) -> None:
    """
    Validate Origin/Referer for cookie-authenticated refresh requests.

    SameSite=Lax/Strict is the primary browser CSRF control. This origin check
    adds defence in depth and becomes mandatory when SameSite=None is used.
    """
    origin = request.headers.get("Origin")
    referer = request.headers.get("Referer")
    candidate = origin or referer

    if not candidate:
        if settings.cookie_samesite == "none" or settings.environment == "production":
            raise AuthorizationError("CSRF validation failed.")
        return

    if not _same_origin(candidate, settings.frontend_url):
        raise AuthorizationError("CSRF validation failed.")


# ---------------------------------------------------------------------------
# POST /auth/signup
# ---------------------------------------------------------------------------
@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=201,
    summary="Register a new user account",
    description=(
        "Create a new CANDIDATE account. Email must be unique. "
        "Only the CANDIDATE role is permitted on self-signup. "
        "Returns a generic error on duplicate email to prevent enumeration."
    ),
)
@limiter.limit(settings.rate_limit_signup)
async def signup(
    request: Request,
    body: SignupRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Register a new user.

    Rate limited: configurable (default 5/minute per IP).
    """
    service = AuthService(db)
    user = await service.signup(
        body,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        request_id=get_request_id(request),
    )
    return AuthResponse(
        success=True,
        message="Account created successfully.",
        user=user,
    )


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------
@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate and obtain tokens",
    description=(
        "Authenticate with email and password. Returns an access token in the "
        "response body and sets a refresh token as an HttpOnly secure cookie. "
        "Returns a generic error for invalid credentials (no user enumeration)."
    ),
)
@limiter.limit(settings.rate_limit_login)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Login endpoint.

    Rate limited: configurable (default 5/minute per IP).
    Returns refresh token as HttpOnly cookie; access token in body.
    """
    service = AuthService(db)
    access_token, raw_refresh, user = await service.login(
        body,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        request_id=get_request_id(request),
    )

    # Set the refresh token cookie BEFORE building the response
    _set_refresh_cookie(response, raw_refresh)

    token_data = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=_ACCESS_TOKEN_EXPIRES_SECONDS,
    )

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(AuthResponse(
            success=True,
            message="Login successful.",
            data=token_data.model_dump(),
            user=user,
        )),
        headers={
            REQUEST_ID_HEADER: get_request_id(request),
            "Set-Cookie": response.headers.get("set-cookie", ""),
        },
    )


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------
@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Rotate refresh token and issue new access token",
    description=(
        "Exchange a valid refresh token for a new access token + rotated "
        "refresh token. The old refresh token is invalidated. If a revoked "
        "refresh token is submitted, all sessions are immediately revoked."
    ),
)
@limiter.limit(settings.rate_limit_refresh)
async def refresh_tokens(
    request: Request,
    response: Response,
    body: RefreshTokenRequest = RefreshTokenRequest(),
    refresh_token_cookie: str | None = Cookie(default=None, alias=_REFRESH_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Refresh token rotation.

    Accepts refresh token from:
    1. HttpOnly cookie (preferred — for browser SPA).
    2. Request body (for non-browser clients).
    Cookie takes precedence over body.
    """
    # Cookie takes precedence over request body
    raw_refresh = refresh_token_cookie or body.refresh_token

    if not raw_refresh:
        raise AuthenticationError("Refresh token is required.")

    if refresh_token_cookie:
        _validate_cookie_csrf(request)

    service = AuthService(db)
    new_access, new_raw_refresh = await service.refresh_tokens(
        raw_refresh,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        request_id=get_request_id(request),
    )

    _set_refresh_cookie(response, new_raw_refresh)

    token_data = TokenResponse(
        access_token=new_access,
        token_type="bearer",
        expires_in=_ACCESS_TOKEN_EXPIRES_SECONDS,
    )

    return JSONResponse(
        status_code=200,
        content=AuthResponse(
            success=True,
            message="Tokens refreshed successfully.",
            data=token_data.model_dump(),
        ).model_dump(),
        headers={
            REQUEST_ID_HEADER: get_request_id(request),
            "Set-Cookie": response.headers.get("set-cookie", ""),
        },
    )


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------
@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout current session",
    description=(
        "Revoke the current session. The refresh token cookie is cleared. "
        "The access token will remain valid until it expires (short TTL). "
        "Always returns 200 even if the session was already revoked."
    ),
)
@limiter.limit("20/minute")
async def logout(
    request: Request,
    response: Response,
    auth: AuthenticatedUser = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revoke the current session."""
    service = AuthService(db)
    await service.logout(
        jti=auth.jti,
        user_id=str(auth.user.id),
        request_id=get_request_id(request),
        ip_address=get_client_ip(request),
    )

    _clear_refresh_cookie(response)

    return MessageResponse(success=True, message="Logged out successfully.")


# ---------------------------------------------------------------------------
# POST /auth/logout-all
# ---------------------------------------------------------------------------
@router.post(
    "/logout-all",
    response_model=MessageResponse,
    summary="Logout all sessions",
    description=(
        "Revoke all active sessions for the authenticated user. "
        "Useful when the user suspects their credentials were compromised."
    ),
)
@limiter.limit("5/minute")
async def logout_all(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revoke all sessions for the current user."""
    service = AuthService(db)
    await service.logout_all(
        user_id=current_user.id,
        request_id=get_request_id(request),
        ip_address=get_client_ip(request),
    )

    _clear_refresh_cookie(response)

    return MessageResponse(
        success=True,
        message="All sessions have been terminated.",
    )


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
    description=(
        "Return the profile of the currently authenticated user. "
        "Never returns internal credential digests, refresh tokens, or secrets."
    ),
)
@limiter.limit("30/minute")
async def get_me(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Return the current user's profile."""
    service = AuthService(db)
    return await service.get_current_user_info(current_user.id)


# ---------------------------------------------------------------------------
# POST /auth/forgot-password
# ---------------------------------------------------------------------------
@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Initiate password reset",
    description=(
        "Send a password reset OTP to the provided email address. "
        "Always returns the same generic response regardless of whether "
        "the email is registered (prevents user enumeration)."
    ),
)
@limiter.limit(settings.rate_limit_forgot_password)
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Initiate password reset.

    SECURITY: Always returns a generic message. The OTP is sent via email
    (out-of-band) — it is NEVER included in this response.
    """
    service = AuthService(db)
    raw_otp = await service.forgot_password(
        body,
        ip_address=get_client_ip(request),
        request_id=get_request_id(request),
    )

    # TODO: Integrate with your email service to send raw_otp to body.email.
    # raw_otp is None if the user does not exist — do not reveal this.
    # Example: await email_service.send_otp(body.email, raw_otp)
    # NEVER log or return raw_otp in this response.

    return MessageResponse(
        success=True,
        message=(
            "If an account with that email exists, a password reset code "
            "has been sent. Please check your email."
        ),
    )


# ---------------------------------------------------------------------------
# POST /auth/verify-otp
# ---------------------------------------------------------------------------
@router.post(
    "/verify-otp",
    response_model=MessageResponse,
    summary="Verify password reset OTP",
    description=(
        "Verify the 6-digit OTP sent during the forgot-password flow. "
        "Rate limited. OTP expires after a configurable timeout. "
        "Too many failed attempts will invalidate the OTP."
    ),
)
@limiter.limit(settings.rate_limit_verify_otp)
async def verify_otp(
    request: Request,
    body: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Verify the password reset OTP."""
    service = AuthService(db)
    await service.verify_otp(
        body,
        ip_address=get_client_ip(request),
        request_id=get_request_id(request),
    )
    return MessageResponse(
        success=True,
        message="OTP verified. You may now reset your password.",
    )


# ---------------------------------------------------------------------------
# POST /auth/reset-password
# ---------------------------------------------------------------------------
@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password using OTP",
    description=(
        "Reset the account password using the verified OTP. "
        "All existing sessions are revoked after a successful reset. "
        "The user must log in again with the new password."
    ),
)
@limiter.limit(settings.rate_limit_reset_password)
async def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Reset the password for an account using a valid OTP."""
    service = AuthService(db)
    await service.reset_password(
        body,
        ip_address=get_client_ip(request),
        request_id=get_request_id(request),
    )
    return MessageResponse(
        success=True,
        message=(
            "Password has been reset successfully. "
            "All existing sessions have been terminated. Please log in again."
        ),
    )
