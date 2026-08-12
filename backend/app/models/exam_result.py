"""
app/models/exam_result.py
==========================
SQLAlchemy 2.0 ORM model for the `exam_results` table.

SECURITY NOTES:
- All numeric score fields are set ONLY by the server-side evaluation engine.
- `status` EVALUATED vs PENDING_EVALUATION is set by the service — not client.
- One result per attempt (UNIQUE on attempt_id).
- `candidate_id` and `exam_id` are denormalized for efficient queries
  without requiring joins to exam_attempts in result listing endpoints.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.exam_attempt import ExamAttempt
    from app.models.user import User
    from app.models.exam import Exam


class ExamResult(UUIDMixin, TimestampMixin, Base):
    """
    Aggregated result for a completed exam attempt.

    Created atomically during submission.
    One result per attempt (UNIQUE on attempt_id).
    """

    __tablename__ = "exam_results"
    __table_args__ = (
        UniqueConstraint("attempt_id", name="uq_exam_results_attempt_id"),
        Index("ix_exam_results_attempt_id", "attempt_id"),
        Index("ix_exam_results_candidate_id", "candidate_id"),
        Index("ix_exam_results_exam_id", "exam_id"),
    )

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_attempts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Denormalized for efficient listing queries.
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
    )

    # --- Score breakdown — all set by server evaluation only ---
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attempted_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    incorrect_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Total possible marks for the exam.
    total_marks: Mapped[float] = mapped_column(
        Numeric(precision=8, scale=2), nullable=False, default=0.0
    )

    # Marks obtained by the candidate.
    score: Mapped[float] = mapped_column(
        Numeric(precision=8, scale=2), nullable=False, default=0.0
    )

    # percentage = (score / total_marks) * 100, rounded to 2dp.
    percentage: Mapped[float] = mapped_column(
        Numeric(precision=5, scale=2), nullable=False, default=0.0
    )

    # EVALUATED | PENDING_EVALUATION
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="EVALUATED",
        server_default="EVALUATED",
    )

    # --- Relationships ---
    attempt: Mapped["ExamAttempt"] = relationship(
        "ExamAttempt", back_populates="result"
    )
    candidate: Mapped["User"] = relationship("User", foreign_keys=[candidate_id])
    exam: Mapped["Exam"] = relationship("Exam", foreign_keys=[exam_id])

    def __repr__(self) -> str:
        return (
            f"<ExamResult id={self.id} attempt_id={self.attempt_id}"
            f" score={self.score}/{self.total_marks} status={self.status}>"
        )
