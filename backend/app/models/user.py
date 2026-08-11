"""
app/models/user.py
==================
SQLAlchemy 2.0 ORM model for the `users` table.

SECURITY NOTES:
- `email` uses PostgreSQL CITEXT for case-insensitive uniqueness without
  needing LOWER() in every query. Requires the citext extension.
- `password_hash` is never returned via API — enforced at the schema layer.
- `is_active = False` prevents login — enforced at the service layer.
- `role_id` is a foreign key to the `roles` table. Users cannot change
  their own role through normal user APIs.
- All timestamps use TIMESTAMPTZ (UTC-aware).

ASSUMPTION: The `citext` PostgreSQL extension is installed via the
Alembic migration (CREATE EXTENSION IF NOT EXISTS citext).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.session import UserSession
    from app.models.otp import PasswordResetOTP


class User(UUIDMixin, TimestampMixin, Base):
    """
    Application user.

    Uniqueness of email is enforced both at the database level (UNIQUE
    constraint on CITEXT column) and at the application level (service
    checks before INSERT).

    NEVER expose `password_hash` through any API response.
    """

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_role_id", "role_id"),
    )

    # CITEXT provides case-insensitive comparison/uniqueness at the DB level.
    # This prevents "Alice@example.com" and "alice@example.com" from being
    # treated as different accounts, which could enable account takeover.
    email: Mapped[str] = mapped_column(
        CITEXT,
        nullable=False,
        unique=True,
    )

    # bcrypt hash — 60 chars + safety margin. Store as VARCHAR(72).
    # NEVER store plaintext. NEVER log this field.
    password_hash: Mapped[str] = mapped_column(
        String(72),
        nullable=False,
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # False = account disabled; inactive users must not be able to log in.
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # --- Relationships ---
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="selectin")
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    otps: Mapped[list["PasswordResetOTP"]] = relationship(
        "PasswordResetOTP", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        # Do NOT include email or any sensitive field in repr
        return f"<User id={self.id} is_active={self.is_active}>"
