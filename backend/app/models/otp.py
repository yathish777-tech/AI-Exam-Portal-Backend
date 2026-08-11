"""
app/models/otp.py
=================
SQLAlchemy 2.0 ORM model for the `password_reset_otps` table.

SECURITY NOTES:
- `otp_hash` stores an HMAC-SHA256 digest of the 6-digit OTP. NEVER the raw OTP.
- `attempt_count` enforces a maximum number of verification attempts.
- `is_used` prevents OTP reuse after successful verification.
- `expires_at` enforces short OTP lifetime.
- When a new OTP is issued for the same user/purpose, previous OTPs are
  invalidated (marked as used) to prevent parallel OTP attacks.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class PasswordResetOTP(UUIDMixin, TimestampMixin, Base):
    """
    One-time password record for password reset verification.

    One row per OTP issuance. Previous OTPs for the same user/purpose
    are invalidated when a new one is issued.
    """

    __tablename__ = "password_reset_otps"
    __table_args__ = (
        Index("ix_otp_user_id", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # HMAC-SHA256 hex of the raw OTP (64 chars).
    # NEVER store the raw OTP value.
    otp_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # OTP purpose — extensible for future flows (e.g. email verification).
    purpose: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="password_reset",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Number of failed verification attempts for this OTP.
    # Exceeding OTP_MAX_ATTEMPTS locks the OTP and triggers security event.
    attempt_count: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
    )

    # True once the OTP has been successfully used. Prevents reuse.
    is_used: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship("User", back_populates="otps")

    @property
    def is_expired(self) -> bool:
        """True if the OTP has passed its expiry time."""
        from datetime import timezone
        return self.expires_at < datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return (
            f"<PasswordResetOTP id={self.id} user_id={self.user_id} "
            f"purpose={self.purpose!r} is_used={self.is_used}>"
        )
