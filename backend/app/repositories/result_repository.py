"""
app/repositories/result_repository.py
=======================================
Database access layer for the `exam_results` table.

SECURITY NOTES:
- Results are created ONLY by the server-side evaluation engine.
  No user-facing endpoint can write to this table directly.
- `score`, `percentage`, and all count fields are set exclusively
  by the evaluation engine — never from client data.
- UNIQUE(attempt_id) prevents duplicate results.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam_result import ExamResult
from app.models.user import User
from app.repositories.base import BaseRepository


class ResultRepository(BaseRepository[ExamResult]):
    """Repository for ExamResult creation and retrieval."""

    model = ExamResult

    @classmethod
    async def get_by_attempt_id(
        cls,
        db: AsyncSession,
        attempt_id: uuid.UUID,
    ) -> ExamResult | None:
        """Return the result for a specific attempt, if it exists."""
        stmt = select(ExamResult).where(ExamResult.attempt_id == attempt_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_attempt_for_candidate(
        cls,
        db: AsyncSession,
        attempt_id: uuid.UUID,
        candidate_id: uuid.UUID,
    ) -> ExamResult | None:
        """
        Return a result by attempt_id, verifying it belongs to the given candidate.

        SECURITY: Prevents IDOR — a candidate can only read their own result.
        """
        stmt = select(ExamResult).where(
            ExamResult.attempt_id == attempt_id,
            ExamResult.candidate_id == candidate_id,
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
    ) -> tuple[list[dict], int]:
        """
        Return paginated results for an exam, joined with candidate email.

        Used by interviewers/admins for the exam results dashboard.
        SECURITY: Only `email` is returned from User — no sensitive fields.
        """
        stmt = (
            select(
                ExamResult,
                User.email.label("candidate_email"),
            )
            .join(User, User.id == ExamResult.candidate_id)
            .where(ExamResult.exam_id == exam_id)
            .order_by(ExamResult.percentage.desc())
            .offset(skip)
            .limit(limit)
        )
        count_stmt = (
            select(func.count())
            .select_from(ExamResult)
            .where(ExamResult.exam_id == exam_id)
        )

        rows_result = await db.execute(stmt)
        count_result = await db.execute(count_stmt)

        rows = rows_result.all()
        total = count_result.scalar_one()

        items = [
            {
                "result": row.ExamResult,
                "candidate_email": row.candidate_email,
            }
            for row in rows
        ]
        return items, total

    @classmethod
    async def create_result(
        cls,
        db: AsyncSession,
        attempt_id: uuid.UUID,
        candidate_id: uuid.UUID,
        exam_id: uuid.UUID,
        total_questions: int,
        attempted_count: int,
        correct_count: int,
        incorrect_count: int,
        total_marks: float,
        score: float,
        percentage: float,
        status: str,
    ) -> ExamResult:
        """
        Create a new ExamResult record.

        Called exclusively by the submission evaluation engine.
        SECURITY: All score fields are computed by the server — never
        accepted from client input.
        """
        exam_result = ExamResult(
            attempt_id=attempt_id,
            candidate_id=candidate_id,
            exam_id=exam_id,
            total_questions=total_questions,
            attempted_count=attempted_count,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            total_marks=total_marks,
            score=score,
            percentage=round(percentage, 2),
            status=status,
        )
        db.add(exam_result)
        await db.flush()
        await db.refresh(exam_result)
        return exam_result
