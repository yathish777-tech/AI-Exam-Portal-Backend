"""
app/models/exam_attempt.py
===========================
SQLAlchemy 2.0 ORM model for the `exam_attempts` table.

SECURITY NOTES:
- UNIQUE(exam_id, candidate_id) ensures one attempt per candidate per exam.
  This constraint is enforced at both DB and application layer.
- `status` transitions are enforced exclusively by service methods.
- `candidate_id` is always set from the authenticated user — never from
  client request body.
- `submitted_at` is set by the server on submission — not from client.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.exam import Exam
    from app.models.user import User
    from app.models.submission import Submission
    from app.models.exam_result import ExamResult


class ExamAttempt(UUIDMixin, TimestampMixin, Base):
    """
    Records a candidate's exam attempt.

    One attempt per candidate per exam (enforced by UNIQUE constraint).
    Lifecycle: IN_PROGRESS → SUBMITTED | ABANDONED
    """

    __tablename__ = "exam_attempts"
    __table_args__ = (
        UniqueConstraint(
            "exam_id", "candidate_id",
            name="uq_exam_attempts_exam_candidate",
        ),
        Index("ix_exam_attempts_exam_id", "exam_id"),
        Index("ix_exam_attempts_candidate_id", "candidate_id"),
        Index("ix_exam_attempts_status", "status"),
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Always set from authenticated user — NEVER from request body.
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # IN_PROGRESS | SUBMITTED | ABANDONED
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="IN_PROGRESS",
        server_default="IN_PROGRESS",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Set by server on submission — never accepted from client.
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # --- Relationships ---
    exam: Mapped["Exam"] = relationship("Exam", back_populates="attempts")
    candidate: Mapped["User"] = relationship("User", foreign_keys=[candidate_id])
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )
    result: Mapped["ExamResult | None"] = relationship(
        "ExamResult",
        back_populates="attempt",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ExamAttempt id={self.id} exam_id={self.exam_id}"
            f" candidate_id={self.candidate_id} status={self.status}>"
        )
