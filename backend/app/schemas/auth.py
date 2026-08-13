"""
app/schemas/auth.py
===================
Pydantic v2 request/response schemas for authentication endpoints.

SECURITY NOTES:
- `model_config = ConfigDict(extra="forbid")` rejects unknown fields,
  preventing mass-assignment attacks (e.g. client sending is_admin=true).
- Password fields have explicit max-length enforcement to prevent
  resource-exhaustion attacks against bcrypt.
- Email is normalized (lowercase, stripped) at the validator level.
- Role in SignupRequest is restricted to CANDIDATE — users cannot
  self-assign ADMIN or INTERVIEWER roles.
- No internal credential digests or OTP values appear in responses.
"""

from __future__ import annotations

import re
import uuid
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.core.constants import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    RoleName,
)


# ---------------------------------------------------------------------------
# Shared validators
# ---------------------------------------------------------------------------

def _normalize_email(email: str) -> str:
    """Lowercase and strip whitespace from email."""
    return email.strip().lower()


def _validate_password_strength(password: str) -> str:
    """
    Validate password against the project's password policy.

    Policy rationale:
    - Minimum length (10) prevents trivial passwords.
    - Maximum length (128) prevents bcrypt resource-exhaustion attacks.
      (bcrypt silently truncates at 72 bytes — we enforce a lower max
      at the application layer to give a clear error message.)
    - We do NOT enforce arbitrary complexity rules (uppercase, special chars)
      as research shows they lead to predictable patterns (Password1!).
      Instead, encourage passphrases and length.
    - We reject passwords that are clearly a single repeated character.
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters."
        )
    if len(password.encode("utf-8")) > PASSWORD_MAX_LENGTH:
        raise ValueError(
            f"Password must not exceed {PASSWORD_MAX_LENGTH} bytes."
        )
    # Reject single-character repeated passwords (e.g. "aaaaaaaaaa")
    if len(set(password)) < 2:
        raise ValueError("Password is too simple. Use a mix of different characters.")
    return password


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class SignupRequest(BaseModel):
    """Request body for POST /auth/signup."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr = Field(
        ...,
        description="Valid email address. Normalized to lowercase.",
        max_length=254,  # RFC 5321 maximum
    )
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        description="Account password. Min 10 chars, max 128 bytes.",
    )
    # Restrict self-registration to CANDIDATE only.
    # ADMIN and INTERVIEWER accounts must be created by an admin.
    role: RoleName = Field(
        default=RoleName.CANDIDATE,
        description="Role for the new account. Only CANDIDATE is allowed on self-signup.",
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return _normalize_email(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)

    @field_validator("role")
    @classmethod
    def restrict_self_signup_role(cls, v: RoleName) -> RoleName:
        """Users may only self-register as CANDIDATE."""
        if v != RoleName.CANDIDATE:
            raise ValueError(
                "Self-registration is only permitted for the CANDIDATE role. "
                "Contact an administrator for other role assignments."
            )
        return v


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr = Field(
        ...,
        max_length=254,
        description="Registered email address.",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=PASSWORD_MAX_LENGTH,
        description="Account password.",
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return _normalize_email(v)


class RefreshTokenRequest(BaseModel):
    """
    Request body for POST /auth/refresh.

    The refresh token may also be provided as an HttpOnly cookie.
    If both are present, the cookie takes precedence.
    """

    model_config = ConfigDict(extra="forbid")

    refresh_token: str | None = Field(
        default=None,
        max_length=200,
        description="Refresh token from the previous login/refresh response. "
                    "If provided as a cookie, this field is optional.",
    )


class ForgotPasswordRequest(BaseModel):
    """Request body for POST /auth/forgot-password."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr = Field(
        ...,
        max_length=254,
        description="Email address of the account to reset.",
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return _normalize_email(v)


class VerifyOTPRequest(BaseModel):
    """Request body for POST /auth/verify-otp."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr = Field(
        ...,
        max_length=254,
        description="Email address associated with the OTP.",
    )
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6-digit one-time password sent to the registered email.",
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return _normalize_email(v)

    @field_validator("otp")
    @classmethod
    def validate_otp_format(cls, v: str) -> str:
        """OTP must be exactly 6 digits."""
        if not re.fullmatch(r"\d{6}", v):
            raise ValueError("OTP must be exactly 6 digits.")
        return v


class ResetPasswordRequest(BaseModel):
    """Request body for POST /auth/reset-password."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr = Field(
        ...,
        max_length=254,
        description="Email address of the account to reset.",
    )
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6-digit OTP from the forgot-password flow.",
    )
    new_password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        description="New password. Must meet password policy requirements.",
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return _normalize_email(v)

    @field_validator("otp")
    @classmethod
    def validate_otp_format(cls, v: str) -> str:
        if not re.fullmatch(r"\d{6}", v):
            raise ValueError("OTP must be exactly 6 digits.")
        return v

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return _validate_password_strength(v)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    """Access token response payload."""

    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer').")
    expires_in: int = Field(..., description="Access token lifetime in seconds.")


class UserResponse(BaseModel):
    """
    Safe user representation for API responses.

    NEVER includes internal credential digests or secrets.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    email: str
    role: str = Field(description="Role name (e.g. CANDIDATE, ADMIN).")
    is_active: bool
    last_login_at: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_role_name(cls, data: object) -> object:
        """
        Extract the role name string from the ORM User object or dict.
        The ORM User has a `role` relationship; we extract `.role.name`.
        """
        if hasattr(data, "role") and hasattr(data.role, "name"):
            # ORM object: convert role relationship to role name string
            role_name = data.role.name
            return {
                "id": data.id,
                "email": data.email,
                "role": role_name,
                "is_active": data.is_active,
                "last_login_at": (
                    data.last_login_at.isoformat() if data.last_login_at else None
                ),
            }
        return data


class AuthResponse(BaseModel):
    """Combined login/signup response."""

    model_config = ConfigDict(extra="forbid")

    success: bool = True
    message: str
    data: TokenResponse | None = None
    user: UserResponse | None = None


class MessageResponse(BaseModel):
    """Generic success/failure response."""

    model_config = ConfigDict(extra="forbid")

    success: bool
    message: str
    error_code: str | None = None
