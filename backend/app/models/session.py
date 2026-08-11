"""
app/models/session.py
=====================
SQLAlchemy 2.0 ORM model for the `sessions` table.

This table tracks refresh-token session families.

SECURITY NOTES:
- `token_family_id` links all rotations from the same login.
- `current_refresh_token_hash` stores the SHA-256 hex of the raw refresh token.
  The raw token is NEVER stored. If the DB is compromised, stored hashes
  cannot be directly replayed as refresh tokens (high entropy raw token).
- `jwt_jti` stores the JTI (JWT ID) issued with this refresh token.
- `revoked_at` is set (not null) when the session is revoked. Revoked
  sessions are kept in the table for audit purposes.
- `ip_address` uses PostgreSQL INET type for proper IP storage.
- All timestamps are TIMESTAMPTZ (UTC-aware).

ASSUMPTION: Model is named `UserSession` to avoid conflict with
SQLAlchemy's own `Session` class.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserSession(UUIDMixin, TimestampMixin, Base):
    """
    Tracks active (and recently revoked) refresh-token sessions.

    One row per refresh-token issuance. Rotation creates a new row in the
    same token family and revokes the previous row, so replay of an old
    refresh token can still be detected.
    """

    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_sessions_user_id", "user_id"),
        Index("ix_sessions_token_family_id", "token_family_id"),
        Index("ix_sessions_jwt_jti", "jwt_jti"),
        Index(
            "ix_sessions_current_refresh_token_hash",
            "current_refresh_token_hash",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_family_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        default=uuid.uuid4,
    )

    # JWT ID of the most recently issued access token for this session.
    # Used to validate that the access token's jti matches a live session.
    jwt_jti: Mapped[str] = mapped_column(
        String(36),  # UUID4 string = 36 chars
        nullable=False,
        unique=True,
        index=True,
    )

    # SHA-256 hex of the raw refresh token (64 chars).
    # NEVER store the raw token.
    current_refresh_token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Null = session is active. Non-null = session has been revoked.
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    @property
    def is_revoked(self) -> bool:
        """True if this session has been revoked."""
        return self.revoked_at is not None

    @property
    def is_expired(self) -> bool:
        """True if this session's refresh token has expired."""
        from datetime import timezone
        return self.expires_at < datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return (
            f"<UserSession id={self.id} user_id={self.user_id} "
            f"revoked={self.revoked_at is not None}>"
        )
