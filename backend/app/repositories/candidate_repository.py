"""
app/repositories/candidate_repository.py
==========================================
Database access layer for the `exam_candidates` join table.

SECURITY NOTES:
- Candidates CANNOT assign themselves — enforced at service layer.
- `assigned_by` is always set from the authenticated user, never from
  client input.
- UNIQUE(exam_id, candidate_id) is enforced at the DB level; the service
  handles the resulting IntegrityError gracefully (skip duplicates).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam_candidate import ExamCandidate
from app.models.user import User


class CandidateRepository:
    """Repository for ExamCandidate assignment operations."""

    @classmethod
    async def is_assigned(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
        candidate_id: uuid.UUID,
    ) -> bool:
        """Return True if the candidate is already assigned to this exam."""
        stmt = select(ExamCandidate).where(
            ExamCandidate.exam_id == exam_id,
            ExamCandidate.candidate_id == candidate_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    @classmethod
    async def assign_candidates(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
        candidate_ids: list[uuid.UUID],
        assigned_by: uuid.UUID,
    ) -> tuple[int, int]:
        """
        Assign multiple candidates to an exam, skipping duplicates.

        Uses ON CONFLICT DO NOTHING so duplicate assignments are silently
        skipped (idempotent).

        Returns:
            tuple[assigned_count, skipped_count]
        """
        if not candidate_ids:
            return 0, 0

        now = datetime.now(timezone.utc)
        rows = [
            {
                "exam_id": exam_id,
                "candidate_id": cid,
                "assigned_by": assigned_by,
                "assigned_at": now,
            }
            for cid in candidate_ids
        ]

        stmt = (
            pg_insert(ExamCandidate)
            .values(rows)
            .on_conflict_do_nothing(
                index_elements=["exam_id", "candidate_id"]
            )
        )
        result = await db.execute(stmt)
        # rowcount = number of rows actually inserted (skipped = total - inserted)
        assigned = result.rowcount if result.rowcount is not None else 0
        skipped = len(candidate_ids) - assigned
        return assigned, skipped

    @classmethod
    async def list_candidates(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[dict], int]:
        """
        Return paginated list of candidates assigned to an exam.

        Joins ExamCandidate with User to return email.

        SECURITY: Only `email` and `id` are returned — never password_hash.
        """
        stmt = (
            select(
                ExamCandidate.candidate_id,
                ExamCandidate.assigned_at,
                ExamCandidate.assigned_by,
                User.email,
            )
            .join(User, User.id == ExamCandidate.candidate_id)
            .where(ExamCandidate.exam_id == exam_id)
            .order_by(ExamCandidate.assigned_at.asc())
            .offset(skip)
            .limit(limit)
        )
        count_stmt = (
            select(func.count())
            .select_from(ExamCandidate)
            .where(ExamCandidate.exam_id == exam_id)
        )

        rows_result = await db.execute(stmt)
        count_result = await db.execute(count_stmt)

        rows = rows_result.all()
        total = count_result.scalar_one()

        items = [
            {
                "candidate_id": row.candidate_id,
                "email": row.email,
                "assigned_at": row.assigned_at,
                "assigned_by": row.assigned_by,
            }
            for row in rows
        ]
        return items, total

    @classmethod
    async def remove_candidate(
        cls,
        db: AsyncSession,
        exam_id: uuid.UUID,
        candidate_id: uuid.UUID,
    ) -> bool:
        """
        Remove a candidate assignment. Returns True if a row was deleted.
        """
        stmt = delete(ExamCandidate).where(
            ExamCandidate.exam_id == exam_id,
            ExamCandidate.candidate_id == candidate_id,
        )
        result = await db.execute(stmt)
        await db.flush()
        return (result.rowcount or 0) > 0
