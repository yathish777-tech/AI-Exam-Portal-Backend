"""
app/models/exam_candidate.py
=============================
SQLAlchemy 2.0 ORM model for the `exam_candidates` table.

This is the assignment join table linking exams to candidates.

SECURITY NOTES:
- UNIQUE(exam_id, candidate_id) prevents duplicate assignments at the DB level.
- `assigned_by` records who performed the assignment for audit purposes.
- Candidates CANNOT assign themselves — enforced at the service layer.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.exam import Exam
    from app.models.user import User


class ExamCandidate(Base):
    """
    Tracks which candidates are assigned to which exams.

    One row = one candidate assignment.
    UNIQUE(exam_id, candidate_id) enforced at DB level to prevent duplicates.
    """

    __tablename__ = "exam_candidates"
    __table_args__ = (
        UniqueConstraint(
            "exam_id", "candidate_id",
            name="uq_exam_candidates_exam_candidate",
        ),
        Index("ix_exam_candidates_exam_id", "exam_id"),
        Index("ix_exam_candidates_candidate_id", "candidate_id"),
    )

    # Composite primary key
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    # Who performed the assignment (interviewer or admin UUID).
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---
    exam: Mapped["Exam"] = relationship("Exam", back_populates="exam_candidates")
    candidate: Mapped["User"] = relationship("User", foreign_keys=[candidate_id])
    assigner: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_by])

    def __repr__(self) -> str:
        return (
            f"<ExamCandidate exam_id={self.exam_id}"
            f" candidate_id={self.candidate_id}>"
        )
