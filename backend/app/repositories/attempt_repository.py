"""
app/repositories/attempt_repository.py
========================================
Database access layer for the `exam_attempts` table.

SECURITY NOTES:
- UNIQUE(exam_id, candidate_id) is enforced at DB level.
  The service must handle IntegrityError → ConflictError.
- `candidate_id` is ALWAYS set from the authenticated user at the service
  layer — never from client request data.
- `status` transitions are enforced exclusively by service methods.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam_attempt import ExamAttempt
from app.repositories.base import BaseRepository


class AttemptRepository(BaseRepository[ExamAttempt]):
    """Repository for ExamAttempt operations."""

    model = ExamAttempt

    @classmethod
    async def get_by_exam_and_candidate(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
        candidate_id: uuid.UUID,
    ) -> ExamAttempt | None:
        """
        Return the existing attempt for a candidate on a specific exam.

        Used to:
        - Detect duplicate attempt (one attempt per candidate per exam).
        - Resume an in-progress attempt.
        """
        stmt = select(ExamAttempt).where(
            ExamAttempt.exam_id == exam_id,
            ExamAttempt.candidate_id == candidate_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id_for_candidate(
        cls,
        db: AsyncSession,
        attempt_id: uuid.UUID,
        candidate_id: uuid.UUID,
    ) -> ExamAttempt | None:
        """
        Return an attempt by ID, verifying it belongs to the given candidate.

        This prevents IDOR where a user could access another candidate's
        attempt by guessing the attempt UUID.
        """
        stmt = select(ExamAttempt).where(
            ExamAttempt.id == attempt_id,
            ExamAttempt.candidate_id == candidate_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def list_by_exam(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ExamAttempt], int]:
        """
        Return paginated attempts for an exam (interviewer/admin view).
        """
        stmt = (
            select(ExamAttempt)
            .where(ExamAttempt.exam_id == exam_id)
            .order_by(ExamAttempt.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        count_stmt = (
            select(func.count())
            .select_from(ExamAttempt)
            .where(ExamAttempt.exam_id == exam_id)
        )

        attempts_result = await db.execute(stmt)
        count_result = await db.execute(count_stmt)
        attempts = list(attempts_result.scalars().all())
        total = count_result.scalar_one()
        return attempts, total
