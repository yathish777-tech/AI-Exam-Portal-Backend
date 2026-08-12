"""
app/repositories/warning_repository.py
========================================
Database operations for the `proctoring_warnings` table.

SECURITY NOTES:
- Candidates cannot create, modify, or delete warnings.
- All candidate-facing list queries are scoped to their own candidate_id.
- Admin/Interviewer list queries may filter by attempt or exam.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.proctoring_warning import ProctoringWarning


class WarningRepository:
    """Data-access layer for ProctoringWarning records."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        *,
        attempt_id: uuid.UUID,
        candidate_id: uuid.UUID,
        violation_type: str,
        severity: str = "LOW",
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProctoringWarning:
        """Insert a new proctoring warning."""
        warning = ProctoringWarning(
            attempt_id=attempt_id,
            candidate_id=candidate_id,
            violation_type=violation_type,
            severity=severity,
            description=description,
            event_metadata=metadata,
        )
        self._db.add(warning)
        await self._db.flush()
        await self._db.refresh(warning)
        return warning

    async def get_by_id(self, warning_id: uuid.UUID) -> ProctoringWarning | None:
        """Return a warning by primary key."""
        result = await self._db.execute(
            select(ProctoringWarning).where(ProctoringWarning.id == warning_id)
        )
        return result.scalar_one_or_none()

    async def list_by_attempt(
        self,
        attempt_id: uuid.UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProctoringWarning]:
        """Return all warnings for a given attempt, newest first."""
        result = await self._db.execute(
            select(ProctoringWarning)
            .where(ProctoringWarning.attempt_id == attempt_id)
            .order_by(ProctoringWarning.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def list_by_candidate(
        self,
        candidate_id: uuid.UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProctoringWarning]:
        """Return all warnings for a given candidate (across attempts), newest first."""
        result = await self._db.execute(
            select(ProctoringWarning)
            .where(ProctoringWarning.candidate_id == candidate_id)
            .order_by(ProctoringWarning.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def list_all(
        self,
        *,
        attempt_id: uuid.UUID | None = None,
        candidate_id: uuid.UUID | None = None,
        violation_type: str | None = None,
        severity: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProctoringWarning]:
        """Return paginated warnings for administrative views."""
        stmt = select(ProctoringWarning)
        if attempt_id is not None:
            stmt = stmt.where(ProctoringWarning.attempt_id == attempt_id)
        if candidate_id is not None:
            stmt = stmt.where(ProctoringWarning.candidate_id == candidate_id)
        if violation_type is not None:
            stmt = stmt.where(ProctoringWarning.violation_type == violation_type)
        if severity is not None:
            stmt = stmt.where(ProctoringWarning.severity == severity)
        result = await self._db.execute(
            stmt.order_by(ProctoringWarning.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def count_all(
        self,
        *,
        attempt_id: uuid.UUID | None = None,
        candidate_id: uuid.UUID | None = None,
        violation_type: str | None = None,
        severity: str | None = None,
    ) -> int:
        """Count warnings matching administrative filters."""
        stmt = select(func.count()).select_from(ProctoringWarning)
        if attempt_id is not None:
            stmt = stmt.where(ProctoringWarning.attempt_id == attempt_id)
        if candidate_id is not None:
            stmt = stmt.where(ProctoringWarning.candidate_id == candidate_id)
        if violation_type is not None:
            stmt = stmt.where(ProctoringWarning.violation_type == violation_type)
        if severity is not None:
            stmt = stmt.where(ProctoringWarning.severity == severity)
        result = await self._db.execute(stmt)
        return result.scalar_one()

    async def count_by_attempt(self, attempt_id: uuid.UUID) -> int:
        """Count total proctoring warnings for an attempt."""
        result = await self._db.execute(
            select(func.count()).where(
                ProctoringWarning.attempt_id == attempt_id
            )
        )
        return result.scalar_one()

    async def count_by_severity(
        self, attempt_id: uuid.UUID, severity: str
    ) -> int:
        """Count warnings of a specific severity for an attempt."""
        result = await self._db.execute(
            select(func.count()).where(
                ProctoringWarning.attempt_id == attempt_id,
                ProctoringWarning.severity == severity,
            )
        )
        return result.scalar_one()
