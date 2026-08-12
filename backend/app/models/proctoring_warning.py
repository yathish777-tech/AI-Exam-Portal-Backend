"""
app/models/proctoring_warning.py
==================================
SQLAlchemy 2.0 ORM model for the `proctoring_warnings` table.

SECURITY NOTES:
- `attempt_id` and `candidate_id` are set server-side only.
- Candidates cannot create, modify, or delete proctoring warnings.
- Severity and violation type are enum-constrained at the service layer.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.exam_attempt import ExamAttempt
    from app.models.user import User


class ProctoringWarning(UUIDMixin, TimestampMixin, Base):
    """
    A proctoring violation event linked to a specific exam attempt.

    Violation types: TAB_SWITCH | FACE_NOT_DETECTED | MULTIPLE_FACES |
                     COPY_PASTE | FULLSCREEN_EXIT | AUDIO_DETECTED
    Severity: LOW | MEDIUM | HIGH | CRITICAL
    """

    __tablename__ = "proctoring_warnings"
    __table_args__ = (
        Index("ix_proctoring_warnings_attempt_id", "attempt_id"),
        Index("ix_proctoring_warnings_candidate_id", "candidate_id"),
        Index("ix_proctoring_warnings_violation_type", "violation_type"),
    )

    # FK to the specific exam attempt being proctored.
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Denormalized for efficient per-candidate queries without joining attempts.
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Violation category — constrained by service layer.
    violation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # LOW | MEDIUM | HIGH | CRITICAL
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="LOW",
        server_default="LOW",
    )

    # Human-readable description of the event.
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Optional metadata: screenshot path, confidence score, browser info, etc.
    event_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    # --- Relationships ---
    attempt: Mapped["ExamAttempt"] = relationship(
        "ExamAttempt", foreign_keys=[attempt_id]
    )
    candidate: Mapped["User"] = relationship("User", foreign_keys=[candidate_id])

    def __repr__(self) -> str:
        return (
            f"<ProctoringWarning id={self.id} attempt_id={self.attempt_id}"
            f" type={self.violation_type} severity={self.severity}>"
        )
