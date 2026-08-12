"""
app/dependencies/auth.py
========================
FastAPI dependency for JWT authentication.

This dependency:
1. Extracts the Bearer token from the Authorization header.
2. Decodes and validates the JWT (algorithm, expiry, type, iss/aud).
3. Looks up the session by JTI to verify the token is associated with
   a live, non-revoked session (provides server-side token invalidation).
4. Loads the user from the database and checks is_active.
5. Returns the authenticated User ORM object.

SECURITY:
- The JWT algorithm is fixed server-side — never accepted from client.
- Role is loaded from the database (via the user.role relationship),
  NOT from the JWT claims. JWT role claim is informational only.
- A missing, expired, tampered, or wrong-type token all raise HTTP 401
  with a generic message (no internal details leaked).
- Authorization header value is NEVER logged.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SecurityEvent
from app.core.exceptions import (
    AccountDisabledError,
    AuthenticationError,
    SessionRevokedError,
    TokenInvalidError,
)
from app.core.logging import log_security_event
from app.core.security import decode_access_token
from app.database.dependencies import get_db
from app.models.user import User
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository

# HTTPBearer extracts the token from "Authorization: Bearer <token>"
# auto_error=False lets us return a custom 401 instead of FastAPI's default.
_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    """Validated authentication context for the current request."""

    user: User
    jti: str
    session_id: uuid.UUID


async def get_current_user_context(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedUser:
    """
    FastAPI dependency: validate JWT and return the authenticated User.

    Usage:
        @router.get("/protected")
        async def protected(auth = Depends(get_current_user_context)):
            ...

    Raises:
        AuthenticationError (401): For any authentication failure.
        AccountDisabledError (401): If the account is disabled.
    """
    request_id: str = getattr(request.state, "request_id", "")

    if credentials is None:
        raise AuthenticationError("Authentication required.")

    token = credentials.credentials

    # 1. Decode and validate the JWT
    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        log_security_event(
            SecurityEvent.TOKEN_VALIDATION_FAILED,
            request_id=request_id,
            ip_address=request.client.host if request.client else "",
            endpoint=str(request.url.path),
            success=False,
            detail=str(exc),  # safe: jose errors don't contain secrets
        )
        raise TokenInvalidError("Authentication token is invalid or has expired.")

    # 2. Extract subject and JTI from payload
    subject = payload.get("sub")
    jti = payload.get("jti")

    if not subject or not jti:
        raise TokenInvalidError("Token payload is missing required claims.")

    # 3. Validate JTI against an active session in the database
    #    This enables server-side session invalidation even for valid JWTs.
    session_repo = SessionRepository(db)
    session = await session_repo.get_by_jti(jti)

    if session is None:
        log_security_event(
            SecurityEvent.SESSION_REVOKED,
            request_id=request_id,
            user_id=subject,
            ip_address=request.client.host if request.client else "",
            endpoint=str(request.url.path),
            success=False,
            detail="JTI not found in active sessions",
        )
        raise SessionRevokedError("Session is not valid. Please log in again.")

    # 4. Load user from the database (fresh role from DB, not from JWT claims)
    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise TokenInvalidError("Token subject is not a valid UUID.")

    if session.user_id != user_id:
        log_security_event(
            SecurityEvent.TOKEN_VALIDATION_FAILED,
            request_id=request_id,
            user_id=subject,
            ip_address=request.client.host if request.client else "",
            endpoint=str(request.url.path),
            success=False,
            detail="Token subject does not match session user",
        )
        raise TokenInvalidError("Authentication token is invalid or has expired.")

    if session.is_expired:
        await session_repo.revoke_session(session.id)
        await db.commit()
        log_security_event(
            SecurityEvent.SESSION_REVOKED,
            request_id=request_id,
            user_id=subject,
            ip_address=request.client.host if request.client else "",
            endpoint=str(request.url.path),
            success=False,
            detail="Session expired",
        )
        raise SessionRevokedError("Session is not valid. Please log in again.")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise AuthenticationError("Authenticated user account no longer exists.")

    # 5. Check account status
    if not user.is_active:
        log_security_event(
            SecurityEvent.ACCOUNT_DISABLED,
            request_id=request_id,
            user_id=str(user.id),
            ip_address=request.client.host if request.client else "",
            endpoint=str(request.url.path),
            success=False,
        )
        raise AccountDisabledError()

    # Store user on request state for downstream logging
    request.state.user_id = str(user.id)

    return AuthenticatedUser(user=user, jti=jti, session_id=session.id)


async def get_current_user(
    auth: AuthenticatedUser = Depends(get_current_user_context),
) -> User:
    """Compatibility dependency: return only the authenticated User."""
    return auth.user
