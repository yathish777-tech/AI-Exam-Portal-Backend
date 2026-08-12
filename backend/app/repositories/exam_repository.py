"""
app/repositories/exam_repository.py
=====================================
Database access layer for the `exams` table.

All methods are class methods that accept an AsyncSession.
Business logic belongs in exam_service.py — this layer is DB-only.

SECURITY NOTES:
- `created_by` is ALWAYS a filter — callers must pass the authenticated
  user_id when querying non-admin endpoints.
- No raw SQL — all queries use SQLAlchemy 2.x select() style.
- IntegrityError is NOT caught here; caught and converted in the service.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam import Exam
from app.models.question import Question
from app.repositories.base import BaseRepository


class ExamRepository(BaseRepository[Exam]):
    """Repository for Exam CRUD and listing operations."""

    model = Exam

    @classmethod
    async def get_by_id_with_owner_check(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
        owner_id: uuid.UUID | None = None,
    ) -> Exam | None:
        """
        Return an exam by ID.

        If `owner_id` is provided, also filters by `created_by` so that
        non-admin users can only fetch their own exams. Pass None for admin
        lookups (no owner check).
        """
        stmt = select(Exam).where(Exam.id == exam_id)
        if owner_id is not None:
            stmt = stmt.where(Exam.created_by == owner_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def list_exams(
        cls,
        db: AsyncSession,
        owner_id: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Exam], int]:
        """
        Return a paginated list of exams.

        Args:
            owner_id: Filter by creator. None = all exams (admin only).
            status:   Optional status filter (DRAFT, PUBLISHED, etc.).
            skip:     Pagination offset.
            limit:    Page size.

        Returns:
            tuple[list[Exam], total_count]
        """
        stmt = select(Exam)
        count_stmt = select(func.count()).select_from(Exam)

        if owner_id is not None:
            stmt = stmt.where(Exam.created_by == owner_id)
            count_stmt = count_stmt.where(Exam.created_by == owner_id)

        if status is not None:
            stmt = stmt.where(Exam.status == status)
            count_stmt = count_stmt.where(Exam.status == status)

        stmt = stmt.order_by(Exam.created_at.desc()).offset(skip).limit(limit)

        exams_result = await db.execute(stmt)
        count_result = await db.execute(count_stmt)
        exams = list(exams_result.scalars().all())
        total = count_result.scalar_one()
        return exams, total

    @classmethod
    async def get_question_count(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
    ) -> int:
        """Return the number of questions for an exam."""
        stmt = select(func.count()).select_from(Question).where(
            Question.exam_id == exam_id
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    @classmethod
    async def list_candidate_exams(
        cls,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Exam], int]:
        """
        Return exams assigned to a candidate via exam_candidates join.
        Used in the candidate's 'my exams' view.
        """
        from app.models.exam_candidate import ExamCandidate

        stmt = (
            select(Exam)
            .join(ExamCandidate, ExamCandidate.exam_id == Exam.id)
            .where(ExamCandidate.candidate_id == candidate_id)
            .where(Exam.status.in_(["PUBLISHED", "SCHEDULED"]))
            .order_by(Exam.scheduled_at.asc().nullslast(), Exam.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        count_stmt = (
            select(func.count())
            .select_from(Exam)
            .join(ExamCandidate, ExamCandidate.exam_id == Exam.id)
            .where(ExamCandidate.candidate_id == candidate_id)
            .where(Exam.status.in_(["PUBLISHED", "SCHEDULED"]))
        )

        exams_result = await db.execute(stmt)
        count_result = await db.execute(count_stmt)
        exams = list(exams_result.scalars().all())
        total = count_result.scalar_one()
        return exams, total
