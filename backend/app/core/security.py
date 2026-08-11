"""
app/core/security.py
====================
All cryptographic operations for the authentication module.

This module contains ONLY security primitives — no business logic,
no database access, no HTTP concerns.

SECURITY NOTES:
- Passwords are hashed with bcrypt. The cost factor is configurable.
- Raw refresh tokens are NEVER stored — only their SHA-256 hashes.
  Refresh tokens have 384-bit entropy so plain SHA-256 is safe.
- OTPs use HMAC-SHA256(server_secret, otp) — NOT plain SHA-256.
  A 6-digit OTP has only 10^6 possibilities; plain SHA-256 is trivially
  brute-forced offline. HMAC requires knowledge of the server secret,
  turning an offline attack into an online one.
- JWT algorithm is configured server-side; never accept it from the client.
- 'alg=none' is explicitly rejected.
- CSPRNG (secrets module / os.urandom) is used for all random material.
- Timing-safe comparison is used for hash verification.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.constants import (
    ACCESS_TOKEN_TYPE,
    OTP_LENGTH,
    PASSWORD_MAX_LENGTH,
)

settings = get_settings()

# ---------------------------------------------------------------------------
# bcrypt context
# ---------------------------------------------------------------------------
# schemes=["bcrypt"] ensures ONLY bcrypt is accepted.
# deprecated="auto" marks all non-current schemes as deprecated
# (useful if you ever migrate hash algorithms in the future).
# ---------------------------------------------------------------------------
_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.bcrypt_rounds,
)


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    IMPORTANT: bcrypt silently truncates inputs > 72 bytes. To prevent
    resource-exhaustion attacks from oversized inputs, callers MUST
    validate the password length before calling this function.
    See PASSWORD_MAX_LENGTH in constants.py.

    Args:
        plain_password: The plaintext password. Never log or store this.

    Returns:
        A bcrypt hash string (60 characters).
    """
    if len(plain_password.encode("utf-8")) > PASSWORD_MAX_LENGTH:
        raise ValueError("Password exceeds maximum allowed length.")
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Uses passlib's constant-time comparison to prevent timing attacks.
    Returns False (not raises) for any verification failure, including
    malformed hash strings, to avoid leaking information.

    Args:
        plain_password: The plaintext password to check. Never log.
        hashed_password: The stored bcrypt hash to verify against.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # passlib raises on malformed hashes; return False to avoid enumeration.
        return False


# ---------------------------------------------------------------------------
# JWT utilities
# ---------------------------------------------------------------------------

def _get_jwt_options(require_exp: bool = True) -> dict:
    """Build the jose decode options dict."""
    return {
        "verify_signature": True,
        "verify_exp": require_exp,
        "verify_iss": bool(settings.jwt_issuer),
        "verify_aud": bool(settings.jwt_audience),
    }


def generate_access_token(
    *,
    subject: str,
    jti: str,
    role: str,
    extra_claims: dict | None = None,
) -> str:
    """
    Generate a signed JWT access token.

    Claims included:
      sub  — user ID (UUID string)
      jti  — unique token ID (for session lookup + replay prevention)
      type — "access" (validated on decode to prevent refresh tokens being
             used as access tokens and vice-versa)
      role — user's role (for informational display only; authoritative
             role is always loaded from the database)
      iat  — issued-at (UTC)
      exp  — expiry (UTC, short-lived)
      iss  — issuer (if configured)
      aud  — audience (if configured)

    NEVER accept the algorithm from the client. Algorithm is fixed here.

    Args:
        subject: User UUID as string.
        jti: Unique JWT ID (UUID4 string). Must match the stored session.
        role: Role name for informational claims (NOT used for authz decisions).
        extra_claims: Additional claims to include (use sparingly).

    Returns:
        Signed JWT string.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload: dict = {
        "sub": subject,
        "jti": jti,
        "type": ACCESS_TOKEN_TYPE,
        "role": role,  # informational only; authz uses DB-loaded role
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    if settings.jwt_issuer:
        payload["iss"] = settings.jwt_issuer
    if settings.jwt_audience:
        payload["aud"] = settings.jwt_audience

    if extra_claims:
        # Prevent overriding reserved claims
        reserved = {"sub", "jti", "type", "role", "iat", "exp", "iss", "aud"}
        safe_extra = {k: v for k, v in extra_claims.items() if k not in reserved}
        payload.update(safe_extra)

    secret = settings.jwt_secret_key.get_secret_value()
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Validates:
      - Signature (using server-side algorithm only)
      - Expiration (exp claim)
      - Token type ("access")
      - Issuer / audience (if configured)

    Raises:
        JWTError: For any validation failure (expired, tampered, malformed,
                  wrong algorithm, wrong type, etc.).

    Returns:
        The decoded payload dictionary.
    """
    # Explicitly specify the algorithm — never allow the client to dictate it.
    # This prevents algorithm confusion / "alg=none" attacks.
    try:
        secret = settings.jwt_secret_key.get_secret_value()

        decode_kwargs: dict = {
            "algorithms": [settings.jwt_algorithm],  # server-side allowlist
            "options": _get_jwt_options(require_exp=True),
        }
        if settings.jwt_audience:
            decode_kwargs["audience"] = settings.jwt_audience

        payload: dict = jwt.decode(token, secret, **decode_kwargs)
    except JWTError:
        raise  # re-raise to let callers produce the correct HTTP error

    # Validate token type to prevent refresh tokens being used as access tokens
    token_type = payload.get("type")
    if token_type != ACCESS_TOKEN_TYPE:
        raise JWTError(
            f"Invalid token type: expected '{ACCESS_TOKEN_TYPE}', got '{token_type}'."
        )

    # Validate required claims
    if not payload.get("sub"):
        raise JWTError("Token missing 'sub' claim.")
    if not payload.get("jti"):
        raise JWTError("Token missing 'jti' claim.")

    return payload


# ---------------------------------------------------------------------------
# Refresh token utilities
# ---------------------------------------------------------------------------

def generate_refresh_token() -> tuple[str, str]:
    """
    Generate a cryptographically secure refresh token.

    The raw token is a URL-safe base64-encoded 48-byte random value
    (384 bits of entropy — well above the 128-bit minimum for refresh tokens).

    STORAGE RULE: Store ONLY the hash. Never store the raw token.

    Returns:
        tuple[raw_token, token_hash]
        - raw_token: The token to send to the client (in HttpOnly cookie).
        - token_hash: SHA-256 hex digest to store in the database.
          SHA-256 is safe here because the raw token has 384-bit entropy
          (no rainbow table or preimage attack is practical).
    """
    raw_token = secrets.token_urlsafe(48)
    token_hash = hash_value(raw_token)
    return raw_token, token_hash


def hash_value(value: str) -> str:
    """
    Compute the SHA-256 hex digest of a string.

    Used ONLY for hashing high-entropy refresh tokens (384-bit entropy).
    Do NOT use this for OTPs — use hmac_otp_hash() instead.

    Args:
        value: The raw value to hash.

    Returns:
        SHA-256 hex digest (64 lowercase hex characters).
    """
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_hash(plain_value: str, stored_hash: str) -> bool:
    """
    Constant-time comparison of a plaintext value against a stored SHA-256 hash.

    Using hmac.compare_digest prevents timing attacks where an attacker
    infers whether a guess is "close" based on response time.

    Args:
        plain_value: The raw value to verify.
        stored_hash: The SHA-256 hex digest stored in the database.

    Returns:
        True if the hash of plain_value matches stored_hash.
    """
    computed = hash_value(plain_value)
    return hmac.compare_digest(computed.encode(), stored_hash.encode())


# ---------------------------------------------------------------------------
# OTP utilities — HMAC-SHA256 (NOT plain SHA-256)
# ---------------------------------------------------------------------------

def hmac_otp_hash(raw_otp: str, server_secret: str) -> str:
    """
    Compute HMAC-SHA256(server_secret, raw_otp).

    WHY HMAC AND NOT SHA-256:
    A 6-digit OTP has only 10^6 = 1,000,000 possible values.
    Plain SHA-256 of all possible values can be precomputed in milliseconds.
    HMAC-SHA256 with the server's OTP_HASH_SECRET means an attacker who
    steals the DB hash ALSO needs the server secret to brute-force offline,
    turning an offline attack into a server-dependent (rate-limited) one.

    Args:
        raw_otp: The plaintext 6-digit OTP. Never store or log.
        server_secret: The server-side secret (JWT_SECRET_KEY).

    Returns:
        HMAC-SHA256 hex digest (64 lowercase hex characters).
    """
    return hmac.new(
        key=server_secret.encode("utf-8"),
        msg=raw_otp.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def generate_otp() -> tuple[str, str]:
    """
    Generate a cryptographically secure numeric OTP and its HMAC-SHA256 hash.

    Uses secrets.randbelow for uniform distribution with no modulo bias.
    The OTP is zero-padded to OTP_LENGTH digits.

    STORAGE RULE: Store ONLY the HMAC hash. Never store or log the raw OTP.

    Returns:
        tuple[raw_otp, otp_hmac_hash]
        - raw_otp: 6-digit string to send via email. Never store or log.
        - otp_hmac_hash: HMAC-SHA256 digest to store in the database.
    """
    raw_otp = str(secrets.randbelow(10**OTP_LENGTH)).zfill(OTP_LENGTH)
    server_secret = settings.otp_hash_secret.get_secret_value()
    otp_hmac = hmac_otp_hash(raw_otp, server_secret)
    return raw_otp, otp_hmac


def verify_otp_hash(plain_otp: str, stored_hash: str) -> bool:
    """
    Verify an OTP input against a stored HMAC-SHA256 digest (constant-time).

    Args:
        plain_otp: The raw OTP string provided by the user.
        stored_hash: The HMAC-SHA256 hex digest from the database.

    Returns:
        True if the OTP is correct.
    """
    server_secret = settings.otp_hash_secret.get_secret_value()
    computed = hmac_otp_hash(plain_otp, server_secret)
    return hmac.compare_digest(computed.encode(), stored_hash.encode())


# ---------------------------------------------------------------------------
# JTI (JWT ID) generation
# ---------------------------------------------------------------------------

def generate_jti() -> str:
    """Generate a UUID4 string for use as a JWT ID (jti claim)."""
    return str(uuid.uuid4())
