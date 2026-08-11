"""
app/services/auth_service.py
=============================
Authentication and authorization business logic.

This layer orchestrates repositories and security utilities. It contains
NO HTTP concerns (no Request/Response objects) and NO direct SQL.

SECURITY ARCHITECTURE:
- Signup: validates uniqueness → hashes password → creates user (atomic)
- Login: normalize → lookup → verify password (constant time) →
         check is_active → create session → generate tokens → update last_login
- Refresh: lookup session by hash → check revoked/expired → detect reuse →
           rotate tokens → update session
- Logout: revoke session by JTI
- Logout-all: revoke all sessions for user
- Forgot password: always returns generic response (no user enumeration) →
                   invalidate old OTPs → generate new OTP → [send email hook]
- Verify OTP: lookup OTP → check expired → check attempts → verify hash →
              mark used
- Reset password: re-verify OTP → hash new password → update password →
                  revoke all sessions

IMPORTANT: The OTP value is returned from `forgot_password` for the caller
(API layer or email service) to deliver out-of-band. It must NEVER be
included in the HTTP response body.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import OTPPurpose, SecurityEvent
from app.core.exceptions import (
    AccountDisabledError,
    AuthenticationError,
    ConflictError,
    OTPError,
    SessionRevokedError,
    TokenInvalidError,
)
from app.core.logging import log_security_event
from app.core.security import (
    generate_access_token,
    generate_jti,
    generate_otp,
    generate_refresh_token,
    hash_password,
    hash_value,
    verify_otp_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.otp_repository import OTPRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    SignupRequest,
    UserResponse,
    VerifyOTPRequest,
)

settings = get_settings()

# Valid bcrypt hash for a non-secret dummy password. Used to keep the
# unknown-email login path close to the wrong-password path.
_DUMMY_PASSWORD_HASH = "$2b$10$oA891Qw7q9NWmwCP0Y0q.eY6.v1T6wNGdVsK9Z3ulSxFkGs14RJtO"


class AuthService:
    """
    Orchestrates authentication flows.

    All methods are async and accept an AsyncSession from the dependency.
    The session is managed (commit/rollback) by the calling layer.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._sessions = SessionRepository(db)
        self._roles = RoleRepository(db)
        self._otps = OTPRepository(db)

    # -----------------------------------------------------------------------
    # Signup
    # -----------------------------------------------------------------------

    async def signup(
        self,
        request: SignupRequest,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_id: str = "",
    ) -> UserResponse:
        """
        Register a new user account.

        Flow:
        1. Resolve the requested role from the database.
        2. Hash the password.
        3. Create the user (atomically — IntegrityError on duplicate email).
        4. Commit and return a safe UserResponse.

        Raises:
            ConflictError: If the email is already registered.
        """
        # 1. Resolve role
        role = await self._roles.get_by_name(request.role.value)
        if role is None:
            # This should not happen if migrations ran correctly.
            raise AuthenticationError(
                "Registration is temporarily unavailable. Please try again later."
            )

        # 2. Hash password
        password_hash = hash_password(request.password)

        # 3. Create user (ConflictError raised by repo on duplicate)
        user = await self._users.create(
            email=request.email,
            password_hash=password_hash,
            role_id=role.id,
        )

        await self._db.commit()
        await self._db.refresh(user)

        log_security_event(
            SecurityEvent.SIGNUP_SUCCESS,
            request_id=request_id,
            user_id=str(user.id),
            ip_address=ip_address or "",
            endpoint="/auth/signup",
        )

        return UserResponse.model_validate(user)

    # -----------------------------------------------------------------------
    # Login
    # -----------------------------------------------------------------------

    async def login(
        self,
        request: LoginRequest,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_id: str = "",
    ) -> tuple[str, str, UserResponse]:
        """
        Authenticate a user and issue tokens.

        Returns:
            tuple[access_token, raw_refresh_token, UserResponse]

        SECURITY:
        - Password verification uses constant-time comparison.
        - User enumeration is prevented by using the same error message
          for "user not found" and "wrong password".
        - The raw refresh token is returned to the caller to set as a cookie.
          It must NOT be logged.
        - last_login_at is updated AFTER successful authentication.
        """
        # 1. Find user — same error for not found vs wrong password
        user = await self._users.get_by_email(request.email)

        # 2. Verify password (constant-time; always run even if user not found
        #    to prevent timing-based user enumeration)
        stored_hash = user.password_hash if user else _DUMMY_PASSWORD_HASH
        password_ok = verify_password(request.password, stored_hash)

        if not user or not password_ok:
            log_security_event(
                SecurityEvent.LOGIN_FAILED,
                request_id=request_id,
                user_id=str(user.id) if user else "",
                ip_address=ip_address or "",
                endpoint="/auth/login",
                success=False,
                detail="Invalid credentials",
            )
            # Generic error — no distinction between wrong email / wrong password
            raise AuthenticationError("Invalid email or password.")

        # 3. Check account status AFTER password verification to prevent
        #    timing-based active account enumeration.
        if not user.is_active:
            log_security_event(
                SecurityEvent.LOGIN_INACTIVE_ACCOUNT,
                request_id=request_id,
                user_id=str(user.id),
                ip_address=ip_address or "",
                endpoint="/auth/login",
                success=False,
            )
            raise AccountDisabledError()

        # 4. Generate tokens
        jti = generate_jti()
        raw_refresh_token, refresh_token_hash = generate_refresh_token()
        access_token = generate_access_token(
            subject=str(user.id),
            jti=jti,
            role=user.role.name,
        )

        # 5. Create session
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        await self._sessions.create_session(
            user_id=user.id,
            jwt_jti=jti,
            current_refresh_token_hash=refresh_token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        # 6. Update last_login_at
        await self._users.update_last_login(user.id)

        await self._db.commit()
        await self._db.refresh(user)

        log_security_event(
            SecurityEvent.LOGIN_SUCCESS,
            request_id=request_id,
            user_id=str(user.id),
            ip_address=ip_address or "",
            endpoint="/auth/login",
        )

        # Return raw_refresh_token to caller — caller sets it as HttpOnly cookie.
        # NEVER log raw_refresh_token.
        return access_token, raw_refresh_token, UserResponse.model_validate(user)

    # -----------------------------------------------------------------------
    # Refresh token rotation
    # -----------------------------------------------------------------------

    async def refresh_tokens(
        self,
        raw_refresh_token: str,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_id: str = "",
    ) -> tuple[str, str]:
        """
        Rotate the refresh token and issue a new access token.

        Flow:
        1. Hash the incoming token to look up the session.
        2. Check if the session is revoked (REUSE DETECTION).
        3. Check if the session has expired.
        4. Generate new access token + new refresh token.
        5. Update the session record atomically.

        REUSE DETECTION: If a revoked session's hash matches the incoming
        token, we revoke ALL sessions for that user and log a security alert.

        Returns:
            tuple[new_access_token, new_raw_refresh_token]
        """
        token_hash = hash_value(raw_refresh_token)
        session = await self._sessions.get_by_refresh_token_hash(token_hash)

        if session is None:
            log_security_event(
                SecurityEvent.REFRESH_TOKEN_INVALID,
                request_id=request_id,
                ip_address=ip_address or "",
                endpoint="/auth/refresh",
                success=False,
                detail="Refresh token not found",
            )
            raise TokenInvalidError("Invalid refresh token.")

        # Reuse detection: session found but already revoked
        if session.is_revoked:
            log_security_event(
                SecurityEvent.REFRESH_TOKEN_REUSE_DETECTED,
                request_id=request_id,
                user_id=str(session.user_id),
                ip_address=ip_address or "",
                endpoint="/auth/refresh",
                success=False,
                detail="Revoked refresh token reuse detected — revoking all sessions",
            )
            # Revoke the full token family — possible token theft.
            await self._sessions.revoke_token_family(session.token_family_id)
            await self._db.commit()
            raise SessionRevokedError(
                "Security alert: token reuse detected. All sessions have been invalidated. "
                "Please log in again."
            )

        # Check expiry
        if session.is_expired:
            log_security_event(
                SecurityEvent.REFRESH_TOKEN_INVALID,
                request_id=request_id,
                user_id=str(session.user_id),
                ip_address=ip_address or "",
                endpoint="/auth/refresh",
                success=False,
                detail="Refresh token expired",
            )
            raise TokenInvalidError("Refresh token has expired. Please log in again.")

        # Load user to get current role (not from token claims)
        user = await self._users.get_by_id(session.user_id)
        if user is None or not user.is_active:
            await self._sessions.revoke_session(session.id)
            await self._db.commit()
            raise AccountDisabledError()

        # Generate new tokens
        new_jti = generate_jti()
        new_raw_refresh, new_refresh_hash = generate_refresh_token()
        new_access_token = generate_access_token(
            subject=str(user.id),
            jti=new_jti,
            role=user.role.name,
        )

        # Rotate: create a new row in the same family and revoke the old row.
        new_expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        await self._sessions.rotate_refresh_token(
            session.id,
            user_id=user.id,
            token_family_id=session.token_family_id,
            new_jti=new_jti,
            new_refresh_token_hash=new_refresh_hash,
            new_expires_at=new_expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self._db.commit()

        log_security_event(
            SecurityEvent.REFRESH_TOKEN_ROTATION,
            request_id=request_id,
            user_id=str(user.id),
            ip_address=ip_address or "",
            endpoint="/auth/refresh",
        )

        return new_access_token, new_raw_refresh

    # -----------------------------------------------------------------------
    # Logout
    # -----------------------------------------------------------------------

    async def logout(
        self,
        jti: str,
        *,
        user_id: str = "",
        request_id: str = "",
        ip_address: str | None = None,
    ) -> None:
        """Revoke the current session (identified by the access token's JTI)."""
        session = await self._sessions.get_by_jti(jti)
        if session:
            await self._sessions.revoke_session(session.id)
            await self._db.commit()

        log_security_event(
            SecurityEvent.LOGOUT,
            request_id=request_id,
            user_id=user_id,
            ip_address=ip_address or "",
            endpoint="/auth/logout",
        )

    async def logout_all(
        self,
        user_id: uuid.UUID,
        *,
        request_id: str = "",
        ip_address: str | None = None,
    ) -> None:
        """Revoke all sessions for a user (logout from all devices)."""
        await self._sessions.revoke_all_user_sessions(user_id)
        await self._db.commit()

        log_security_event(
            SecurityEvent.LOGOUT_ALL,
            request_id=request_id,
            user_id=str(user_id),
            ip_address=ip_address or "",
            endpoint="/auth/logout-all",
        )

    # -----------------------------------------------------------------------
    # Current user
    # -----------------------------------------------------------------------

    async def get_current_user_info(self, user_id: uuid.UUID) -> UserResponse:
        """Return the safe public profile of the authenticated user."""
        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("User account not found or is disabled.")
        return UserResponse.model_validate(user)

    # -----------------------------------------------------------------------
    # Forgot password
    # -----------------------------------------------------------------------

    async def forgot_password(
        self,
        request: ForgotPasswordRequest,
        *,
        ip_address: str | None = None,
        request_id: str = "",
    ) -> str | None:
        """
        Initiate password reset for an email address.

        SECURITY: Always returns a generic success message regardless of
        whether the email exists — prevents user enumeration.

        Returns:
            The raw OTP string if the user exists (for the email service
            to deliver out-of-band), or None if the user does not exist.

        IMPORTANT: The raw OTP is NEVER included in the HTTP response.
        The caller is responsible for sending it via email and discarding it.
        """
        user = await self._users.get_by_email(request.email)

        log_security_event(
            SecurityEvent.PASSWORD_RESET_REQUESTED,
            request_id=request_id,
            user_id=str(user.id) if user else "",
            ip_address=ip_address or "",
            endpoint="/auth/forgot-password",
        )

        if user is None or not user.is_active:
            # Return None silently — the API layer returns the same generic message
            return None

        # Invalidate any existing OTPs for this user+purpose
        await self._otps.invalidate_user_otps(user.id, OTPPurpose.PASSWORD_RESET)

        # Generate a new OTP — only the hash goes to the DB
        raw_otp, otp_hash = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.otp_expire_minutes
        )
        await self._otps.create_otp(
            user_id=user.id,
            otp_hash=otp_hash,
            purpose=OTPPurpose.PASSWORD_RESET,
            expires_at=expires_at,
        )
        await self._db.commit()

        # Return the raw OTP to the caller (email service).
        # raw_otp must NEVER be logged or included in the HTTP response.
        return raw_otp

    # -----------------------------------------------------------------------
    # Verify OTP
    # -----------------------------------------------------------------------

    async def verify_otp(
        self,
        request: VerifyOTPRequest,
        *,
        ip_address: str | None = None,
        request_id: str = "",
    ) -> bool:
        """
        Verify a password-reset OTP.

        Returns True if valid (for the reset-password flow to proceed).

        SECURITY:
        - Attempt count is incremented on every failure.
        - After OTP_MAX_ATTEMPTS failures, the OTP is marked as used
          (invalidated) — the user must request a new one.
        - Constant-time hash comparison prevents timing attacks.
        - The same generic error is returned for expired, used,
          wrong OTP, and max-attempts — prevents oracle attacks.
        """
        user = await self._users.get_by_email(request.email)
        if user is None:
            # Return generic error to prevent enumeration
            raise OTPError("OTP verification failed.")

        otp_record = await self._otps.get_latest_active(
            user.id, OTPPurpose.PASSWORD_RESET
        )

        if otp_record is None:
            log_security_event(
                SecurityEvent.PASSWORD_RESET_OTP_FAILED,
                request_id=request_id,
                user_id=str(user.id),
                ip_address=ip_address or "",
                success=False,
                detail="No active OTP found",
            )
            raise OTPError("OTP verification failed.")

        # Check max attempts
        if otp_record.attempt_count >= settings.otp_max_attempts:
            await self._otps.mark_used(otp_record.id)
            await self._db.commit()
            log_security_event(
                SecurityEvent.PASSWORD_RESET_OTP_MAX_ATTEMPTS,
                request_id=request_id,
                user_id=str(user.id),
                ip_address=ip_address or "",
                success=False,
            )
            raise OTPError(
                "Too many failed attempts. Please request a new password reset code."
            )

        # Verify OTP hash (constant-time)
        if not verify_otp_hash(request.otp, otp_record.otp_hash):
            await self._otps.increment_attempts(otp_record.id)
            await self._db.commit()
            log_security_event(
                SecurityEvent.PASSWORD_RESET_OTP_FAILED,
                request_id=request_id,
                user_id=str(user.id),
                ip_address=ip_address or "",
                success=False,
                detail="Incorrect OTP",
            )
            raise OTPError("OTP verification failed.")

        log_security_event(
            SecurityEvent.PASSWORD_RESET_OTP_VERIFIED,
            request_id=request_id,
            user_id=str(user.id),
            ip_address=ip_address or "",
        )

        # Note: we do NOT mark the OTP as used here.
        # It is marked used by reset_password() to ensure atomicity.
        # The OTP is valid for the reset step in the same flow.
        return True

    # -----------------------------------------------------------------------
    # Reset password
    # -----------------------------------------------------------------------

    async def reset_password(
        self,
        request: ResetPasswordRequest,
        *,
        ip_address: str | None = None,
        request_id: str = "",
    ) -> None:
        """
        Reset a user's password using a verified OTP.

        Flow:
        1. Re-verify the OTP (atomic with the password update).
        2. Hash the new password.
        3. Update the password_hash.
        4. Mark OTP as used (prevent reuse).
        5. Revoke all existing sessions (force re-login after reset).
        6. Commit atomically.

        SECURITY: Sessions are revoked after password reset to prevent
        an attacker who obtained the old password from maintaining access.
        """
        user = await self._users.get_by_email(request.email)
        if user is None:
            raise AuthenticationError("Invalid request.")

        otp_record = await self._otps.get_latest_active(
            user.id, OTPPurpose.PASSWORD_RESET
        )

        if otp_record is None:
            raise OTPError("OTP has expired or is invalid. Please request a new one.")

        # Check max attempts again (guard against race between verify and reset)
        if otp_record.attempt_count >= settings.otp_max_attempts:
            await self._otps.mark_used(otp_record.id)
            await self._db.commit()
            raise OTPError(
                "Too many failed attempts. Please request a new password reset code."
            )

        # Re-verify OTP hash
        if not verify_otp_hash(request.otp, otp_record.otp_hash):
            await self._otps.increment_attempts(otp_record.id)
            await self._db.commit()
            raise OTPError("OTP verification failed.")

        # Hash new password
        new_hash = hash_password(request.new_password)

        # Atomic update: password + OTP invalidation + session revocation
        await self._users.update_password(user.id, new_hash)
        await self._otps.mark_used(otp_record.id)
        await self._sessions.revoke_all_user_sessions(user.id)

        await self._db.commit()

        log_security_event(
            SecurityEvent.PASSWORD_RESET_SUCCESS,
            request_id=request_id,
            user_id=str(user.id),
            ip_address=ip_address or "",
            endpoint="/auth/reset-password",
        )
