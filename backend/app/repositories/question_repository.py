"""
app/repositories/question_repository.py
=========================================
Database access layer for the `questions` table.

SECURITY NOTES:
- `exam_id` is always verified at the service layer before write operations.
- `options` JSONB is stored and retrieved as-is — validation happens at
  the schema/service layer, not here.
- No raw SQL — all queries use SQLAlchemy 2.x select() style.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question
from app.repositories.base import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    """Repository for Question CRUD and listing operations."""

    model = Question

    @classmethod
    async def list_by_exam(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
    ) -> list[Question]:
        """
        Return all questions for an exam, ordered by order_number.

        Returns the full list (no pagination) since an exam's question count
        is bounded (practical limit is <500 for any real exam).
        """
        stmt = (
            select(Question)
            .where(Question.exam_id == exam_id)
            .order_by(Question.order_number.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_max_order_number(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
    ) -> int:
        """
        Return the current highest order_number for questions in an exam.
        Used to auto-assign the next order_number when not provided.
        Returns 0 if no questions exist yet.
        """
        stmt = select(func.max(Question.order_number)).where(
            Question.exam_id == exam_id
        )
        result = await db.execute(stmt)
        max_order = result.scalar_one_or_none()
        return max_order if max_order is not None else 0

    @classmethod
    async def get_by_id_for_exam(
        cls,
        db: AsyncSession,
        question_id: uuid.UUID,
        exam_id: uuid.UUID,
    ) -> Question | None:
        """
        Return a question by ID, verifying it belongs to the given exam.

        This prevents IDOR where a user could read/modify a question from
        a different exam by guessing the question UUID.
        """
        stmt = select(Question).where(
            Question.id == question_id,
            Question.exam_id == exam_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def count_by_exam(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
    ) -> int:
        """Return the total number of questions for an exam."""
        stmt = select(func.count()).select_from(Question).where(
            Question.exam_id == exam_id
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    @classmethod
    async def get_total_marks(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
    ) -> float:
        """
        Return the sum of all marks for questions in an exam.
        Used during result calculation.
        """
        stmt = select(func.sum(Question.marks)).where(
            Question.exam_id == exam_id
        )
        result = await db.execute(stmt)
        total = result.scalar_one_or_none()
        return float(total) if total is not None else 0.0
