"""
app/models/exam.py
==================
SQLAlchemy 2.0 ORM model for the `exams` table.

SECURITY NOTES:
- `created_by` is set ONLY from the authenticated user at the service layer.
  It is never accepted from client request bodies.
- Status transitions are enforced exclusively by service methods —
  never via direct field update from request data.
- `config` is a JSONB blob for flexible exam configuration (e.g. shuffle
  questions, show results immediately). Validate contents in the service.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.question import Question
    from app.models.exam_candidate import ExamCandidate
    from app.models.exam_attempt import ExamAttempt


class Exam(UUIDMixin, TimestampMixin, Base):
    """
    Represents a single examination created by an interviewer.

    Lifecycle: DRAFT → PUBLISHED → SCHEDULED (optional) → COMPLETED
    """

    __tablename__ = "exams"
    __table_args__ = (
        Index("ix_exams_created_by", "created_by"),
        Index("ix_exams_status", "status"),
        Index("ix_exams_scheduled_at", "scheduled_at"),
    )

    # Owner — always set from authenticated user, NEVER from request body.
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Duration in minutes. Must be > 0 if set.
    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Exam status — transitions enforced by service layer.
    # Stored as VARCHAR to avoid costly Alembic enum migrations on name changes.
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="DRAFT",
        server_default="DRAFT",
    )

    # When the exam is scheduled to start (optional).
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Flexible JSONB config (shuffle_questions, show_results_immediately, etc.)
    config: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # --- Relationships ---
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="exam",
        cascade="all, delete-orphan",
        order_by="Question.order_number",
    )
    exam_candidates: Mapped[list["ExamCandidate"]] = relationship(
        "ExamCandidate",
        back_populates="exam",
        cascade="all, delete-orphan",
    )
    attempts: Mapped[list["ExamAttempt"]] = relationship(
        "ExamAttempt",
        back_populates="exam",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Exam id={self.id} title={self.title!r} status={self.status}>"
