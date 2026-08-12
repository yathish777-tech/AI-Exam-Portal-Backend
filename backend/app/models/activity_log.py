"""
app/models/activity_log.py
============================
SQLAlchemy 2.0 ORM model for the `activity_logs` table.

SECURITY NOTES:
- Activity logs are append-only — no UPDATE or DELETE is permitted.
- `actor_id` is always set from the authenticated user server-side.
- Log entries must never contain raw passwords, tokens, or secrets.
- ADMIN-only read access enforced at the service/router layer.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class ActivityLog(UUIDMixin, TimestampMixin, Base):
    """
    An immutable audit log entry recording a user action.

    Covers: exam lifecycle events, candidate assignments, user management
    actions, settings changes, and proctoring events.

    NEVER include plaintext passwords, tokens, or PII beyond user_id.
    """

    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_actor_id", "actor_id"),
        Index("ix_activity_logs_action", "action"),
        Index("ix_activity_logs_resource_type", "resource_type"),
        Index("ix_activity_logs_created_at", "created_at"),
    )

    # Who performed the action. NULL = system-generated event.
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Action name — use SecurityEvent constants where possible.
    # e.g. "EXAM_CREATED", "USER_DEACTIVATED", "CANDIDATE_ASSIGNED"
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Type of resource affected: "exam", "user", "question", "attempt", etc.
    resource_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # UUID of the affected resource (exam_id, user_id, etc.).
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Human-readable summary for admin display.
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Optional JSONB payload: diff, old/new values, etc.
    # Must NOT contain passwords, tokens, or raw secrets.
    extra: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # IP address of the actor at time of action.
    ip_address: Mapped[str | None] = mapped_column(
        String(45),  # supports IPv6
        nullable=True,
    )

    # --- Relationships ---
    actor: Mapped["User | None"] = relationship("User", foreign_keys=[actor_id])

    def __repr__(self) -> str:
        return (
            f"<ActivityLog id={self.id} action={self.action!r}"
            f" actor_id={self.actor_id}>"
        )
