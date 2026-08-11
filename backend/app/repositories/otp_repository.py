"""
app/repositories/otp_repository.py
=====================================
Database operations for the `password_reset_otps` table.

SECURITY NOTES:
- All OTP hashes stored are HMAC-SHA256 digests — never raw OTP values.
- `invalidate_user_otps` must be called BEFORE creating a new OTP to
  prevent parallel OTP attacks where an attacker generates many OTPs
  and brute-forces all active ones simultaneously.
- `increment_attempts` uses a DB-side counter for atomic increment
  safety in concurrent environments.
- `get_latest_active` returns the single most recently created, non-used,
  non-expired OTP for a user+purpose combination.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.otp import PasswordResetOTP


class OTPRepository:
    """Data-access layer for PasswordResetOTP records."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_otp(
        self,
        *,
        user_id: uuid.UUID,
        otp_hash: str,
        purpose: str,
        expires_at: datetime,
    ) -> PasswordResetOTP:
        """Insert a new OTP record. Returns the created record."""
        otp = PasswordResetOTP(
            user_id=user_id,
            otp_hash=otp_hash,
            purpose=purpose,
            expires_at=expires_at,
            attempt_count=0,
            is_used=False,
        )
        self._db.add(otp)
        await self._db.flush()
        await self._db.refresh(otp)
        return otp

    async def get_latest_active(
        self,
        user_id: uuid.UUID,
        purpose: str,
    ) -> PasswordResetOTP | None:
        """
        Return the most recently created active (non-used, non-expired) OTP
        for the given user and purpose.

        Returns None if no active OTP exists.
        """
        now = datetime.now(timezone.utc)
        result = await self._db.execute(
            select(PasswordResetOTP)
            .where(
                PasswordResetOTP.user_id == user_id,
                PasswordResetOTP.purpose == purpose,
                PasswordResetOTP.is_used.is_(False),
                PasswordResetOTP.expires_at > now,
            )
            .order_by(PasswordResetOTP.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def invalidate_user_otps(
        self, user_id: uuid.UUID, purpose: str
    ) -> None:
        """
        Mark all existing active OTPs for user+purpose as used.

        Called BEFORE creating a new OTP to prevent parallel OTP attacks.
        This is an idempotent operation.
        """
        await self._db.execute(
            update(PasswordResetOTP)
            .where(
                PasswordResetOTP.user_id == user_id,
                PasswordResetOTP.purpose == purpose,
                PasswordResetOTP.is_used.is_(False),
            )
            .values(is_used=True)
        )
        await self._db.flush()

    async def mark_used(self, otp_id: uuid.UUID) -> None:
        """Mark a specific OTP as used to prevent reuse."""
        await self._db.execute(
            update(PasswordResetOTP)
            .where(PasswordResetOTP.id == otp_id)
            .values(is_used=True)
        )
        await self._db.flush()

    async def increment_attempts(self, otp_id: uuid.UUID) -> None:
        """Atomically increment the attempt counter for an OTP."""
        from sqlalchemy import text

        await self._db.execute(
            update(PasswordResetOTP)
            .where(PasswordResetOTP.id == otp_id)
            .values(attempt_count=PasswordResetOTP.attempt_count + 1)
        )
        await self._db.flush()

    async def get_by_id(self, otp_id: uuid.UUID) -> PasswordResetOTP | None:
        """Return a specific OTP record by its ID."""
        result = await self._db.execute(
            select(PasswordResetOTP).where(PasswordResetOTP.id == otp_id)
        )
        return result.scalar_one_or_none()
