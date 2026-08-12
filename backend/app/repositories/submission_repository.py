"""
app/repositories/submission_repository.py
===========================================
Database access layer for the `submissions` table (individual answers).

KEY DESIGN: PostgreSQL upsert (ON CONFLICT DO UPDATE) for auto-save.
- UNIQUE(attempt_id, question_id) means one answer per question per attempt.
- Repeated calls to save_answer() update the existing row (idempotent).

SECURITY NOTES:
- `is_correct` and `score_awarded` are NEVER set by save_answer().
  They are set only by evaluate_answer() during submission.
- `answer_data` is stored as JSONB; structure is validated at service layer.
- `attempt_id` is always verified against the authenticated user at service.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.submission import Submission
from app.repositories.base import BaseRepository


class SubmissionRepository(BaseRepository[Submission]):
    """Repository for Submission (answer) upsert and query operations."""

    model = Submission

    @classmethod
    async def upsert_answer(
        cls,
        db: AsyncSession,
        attempt_id: uuid.UUID,
        question_id: uuid.UUID,
        answer_data: dict[str, Any],
    ) -> Submission:
        """
        Insert or update an answer for a question in an attempt.

        Uses PostgreSQL ON CONFLICT DO UPDATE so repeated auto-saves
        update the existing row atomically.

        SECURITY: `is_correct` and `score_awarded` are NOT set here.
        They are set only during evaluation after submission.
        """
        stmt = (
            pg_insert(Submission)
            .values(
                id=uuid.uuid4(),
                attempt_id=attempt_id,
                question_id=question_id,
                answer_data=answer_data,
                is_correct=None,
                score_awarded=None,
            )
            .on_conflict_do_update(
                constraint="uq_submissions_attempt_question",
                set_={
                    "answer_data": answer_data,
                    # Reset evaluation fields on re-save (candidate changed answer)
                    "is_correct": None,
                    "score_awarded": None,
                },
            )
            .returning(Submission)
        )
        result = await db.execute(stmt)
        await db.flush()
        row = result.fetchone()
        # Re-fetch to get a proper ORM instance
        if row is None:
            # Fallback: fetch the existing row
            fetch_stmt = select(Submission).where(
                Submission.attempt_id == attempt_id,
                Submission.question_id == question_id,
            )
            fetch_result = await db.execute(fetch_stmt)
            return fetch_result.scalar_one()
        return row[0]

    @classmethod
    async def list_by_attempt(
        cls,
        db: AsyncSession,
        attempt_id: uuid.UUID,
    ) -> list[Submission]:
        """
        Return all submissions (answers) for a given attempt.
        Used during evaluation and result retrieval.
        """
        stmt = (
            select(Submission)
            .where(Submission.attempt_id == attempt_id)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def set_evaluation(
        cls,
        db: AsyncSession,
        submission_id: uuid.UUID,
        is_correct: bool,
        score_awarded: float,
    ) -> None:
        """
        Set the evaluation result for a submission.

        Called ONLY by the evaluation engine during submission processing.
        SECURITY: This method is NEVER called from user-facing request handlers.
        """
        stmt = (
            update(Submission)
            .where(Submission.id == submission_id)
            .values(is_correct=is_correct, score_awarded=score_awarded)
        )
        await db.execute(stmt)

    @classmethod
    async def get_by_attempt_and_question(
        cls,
        db: AsyncSession,
        attempt_id: uuid.UUID,
        question_id: uuid.UUID,
    ) -> Submission | None:
        """Return a specific submission by attempt + question combo."""
        stmt = select(Submission).where(
            Submission.attempt_id == attempt_id,
            Submission.question_id == question_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
