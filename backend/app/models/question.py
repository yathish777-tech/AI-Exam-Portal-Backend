"""
app/models/question.py
======================
SQLAlchemy 2.0 ORM model for the `questions` table.

SECURITY NOTES:
- `options` JSONB stores MCQ choices and the correct answer index/key.
  The correct answer MUST be stored server-side — never derived from client.
- `marks` must be > 0 (enforced at service layer and DB check constraint).
- `exam_id` is always verified against the authenticated owner before writes.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.exam import Exam
    from app.models.submission import Submission


class Question(UUIDMixin, TimestampMixin, Base):
    """
    A single question belonging to an exam.

    MCQ questions use `options` JSONB with structure:
        {
          "choices": ["Option A", "Option B", "Option C", "Option D"],
          "correct_index": 0   # 0-based index into choices
        }

    The `correct_index` is NEVER returned to candidates — only to
    interviewers and during server-side evaluation.
    """

    __tablename__ = "questions"
    __table_args__ = (
        Index("ix_questions_exam_id", "exam_id"),
        Index("ix_questions_exam_id_order", "exam_id", "order_number"),
        CheckConstraint("marks > 0", name="ck_questions_marks_positive"),
        CheckConstraint("order_number >= 1", name="ck_questions_order_positive"),
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Question type: MCQ | SHORT_ANSWER | CODING | FILE
    question_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # The question text / prompt.
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Points awarded for a correct answer. Must be > 0.
    marks: Mapped[float] = mapped_column(
        Numeric(precision=6, scale=2),
        nullable=False,
        default=1.0,
    )

    # Display order within the exam (1-based).
    order_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    # MCQ: {"choices": [...], "correct_index": int}
    # SHORT_ANSWER: None or {"expected_keywords": [...]}
    # CODING / FILE: None or config dict
    options: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # --- Relationships ---
    exam: Mapped["Exam"] = relationship("Exam", back_populates="questions")
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Question id={self.id} type={self.question_type}"
            f" exam_id={self.exam_id} order={self.order_number}>"
        )
