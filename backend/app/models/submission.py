"""
app/models/submission.py
=========================
SQLAlchemy 2.0 ORM model for the `submissions` table (individual answers).

SECURITY NOTES:
- UNIQUE(attempt_id, question_id) ensures one answer record per question
  per attempt. The PostgreSQL upsert (ON CONFLICT DO UPDATE) uses this.
- `is_correct` and `score_awarded` are set ONLY by the server-side
  evaluation engine — never by clients.
- `answer_data` is a JSONB blob. For MCQ: {"selected_index": 0}.
  For SHORT_ANSWER: {"text": "..."}.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.exam_attempt import ExamAttempt
    from app.models.question import Question


class Submission(UUIDMixin, TimestampMixin, Base):
    """
    An individual answer submitted (or auto-saved) by a candidate.

    One row per question per attempt.
    UNIQUE(attempt_id, question_id) enforced at DB level.
    PostgreSQL ON CONFLICT DO UPDATE is used for upsert in the repository.
    """

    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint(
            "attempt_id", "question_id",
            name="uq_submissions_attempt_question",
        ),
        Index("ix_submissions_attempt_id", "attempt_id"),
        Index("ix_submissions_question_id", "question_id"),
    )

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Candidate's answer. Structure depends on question_type:
    # MCQ:          {"selected_index": 0}
    # SHORT_ANSWER: {"text": "The answer is ..."}
    # CODING:       {"code": "def foo(): ...", "language": "python"}
    # FILE:         {"file_path": "uploads/attempt_id/filename"}
    answer_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Set by server evaluation only — never from client.
    is_correct: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    # Points awarded — set by server evaluation only.
    score_awarded: Mapped[float | None] = mapped_column(
        Numeric(precision=6, scale=2),
        nullable=True,
    )

    # --- Relationships ---
    attempt: Mapped["ExamAttempt"] = relationship(
        "ExamAttempt", back_populates="submissions"
    )
    question: Mapped["Question"] = relationship(
        "Question", back_populates="submissions"
    )

    def __repr__(self) -> str:
        return (
            f"<Submission id={self.id} attempt_id={self.attempt_id}"
            f" question_id={self.question_id} correct={self.is_correct}>"
        )
