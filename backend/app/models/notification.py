"""
app/models/notification.py
===========================
SQLAlchemy 2.0 ORM model for the `notifications` table.

SECURITY NOTES:
- `user_id` is always the recipient — set server-side only.
- `is_read` is toggled only by the owning user (enforced at service layer).
- Never expose notification bodies from other users (IDOR guard in service).
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Notification(UUIDMixin, TimestampMixin, Base):
    """
    A notification delivered to a specific user.

    Examples: exam assigned, result published, proctoring alert.
    Notifications are created server-side — never by the recipient.
    """

    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_user_id_is_read", "user_id", "is_read"),
    )

    # Recipient — always set by server, never from request body.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Notification category: EXAM_ASSIGNED | RESULT_PUBLISHED | PROCTORING | SYSTEM
    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Optional reference to a related resource (exam_id, attempt_id, etc.)
    reference_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Type of the referenced entity (e.g. "exam", "attempt", "result")
    reference_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return (
            f"<Notification id={self.id} user_id={self.user_id}"
            f" type={self.notification_type} read={self.is_read}>"
        )
