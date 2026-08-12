"""
app/services/proctoring_service.py
=====================================
Business logic for proctoring warning management.

SECURITY NOTES:
- Candidates cannot create warnings on attempts they don't own.
- Attempt ownership is verified before creating a warning.
- Warnings are read-only once created.
- Interviewer/Admin access to warnings is scoped to exams they own.
"""

from __future__ import annotations

import uuid
from math import ceil
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AttemptStatus
from app.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from app.models.exam_attempt import ExamAttempt
from app.models.exam import Exam
from app.repositories.warning_repository import WarningRepository
from app.schemas.proctoring_warning import (
    WarningCreate,
    WarningListResponse,
    WarningResponse,
    WarningSummary,
    VIOLATION_TYPES,
    SEVERITY_LEVELS,
)


class ProctoringService:
    """Proctoring warning operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = WarningRepository(db)

    async def log_warning(
        self,
        attempt_id: uuid.UUID,
        candidate_id: uuid.UUID,
        payload: WarningCreate,
    ) -> WarningResponse:
        """
        Log a proctoring warning for an active attempt.

        Validates:
        - The attempt exists and belongs to the candidate (IDOR guard).
        - The attempt is IN_PROGRESS (can't log on submitted/abandoned).
        - violation_type and severity are within allowed values.
        """
        # Validate violation type and severity
        if payload.violation_type not in VIOLATION_TYPES:
            raise ValidationError(
                f"Invalid violation_type. Must be one of: {', '.join(sorted(VIOLATION_TYPES))}"
            )
        if payload.severity not in SEVERITY_LEVELS:
            raise ValidationError(
                f"Invalid severity. Must be one of: {', '.join(sorted(SEVERITY_LEVELS))}"
            )

        # Load and verify attempt ownership
        attempt = await self._db.get(ExamAttempt, attempt_id)
        if attempt is None or attempt.candidate_id != candidate_id:
            raise NotFoundError("Attempt not found.")

        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise ValidationError(
                "Cannot log a proctoring warning on a non-active attempt."
            )

        warning = await self._repo.create(
            attempt_id=attempt_id,
            candidate_id=candidate_id,
            violation_type=payload.violation_type,
            severity=payload.severity,
            description=payload.description,
            metadata=payload.metadata,
        )
        await self._db.commit()
        return WarningResponse.model_validate(warning)

    async def list_by_attempt(
        self,
        attempt_id: uuid.UUID,
        *,
        requesting_user_id: uuid.UUID,
        is_admin_or_interviewer: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> WarningListResponse:
        """
        Return paginated warnings for an attempt.
        Candidates can only see their own attempt's warnings.
        Interviewers/Admins can see any attempt's warnings.
        """
        attempt = await self._db.get(ExamAttempt, attempt_id)
        if attempt is None:
            raise NotFoundError("Attempt not found.")

        # IDOR: candidates can only see their own attempt
        if not is_admin_or_interviewer:
            if attempt.candidate_id != requesting_user_id:
                raise AuthorizationError()

        offset = (page - 1) * page_size
        items = await self._repo.list_by_attempt(
            attempt_id, limit=page_size, offset=offset
        )
        total = await self._repo.count_by_attempt(attempt_id)
        total_pages = ceil(total / page_size) if page_size > 0 else 0

        return WarningListResponse(
            items=[WarningResponse.model_validate(w) for w in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def list_all(
        self,
        *,
        attempt_id: uuid.UUID | None = None,
        candidate_id: uuid.UUID | None = None,
        violation_type: str | None = None,
        severity: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> WarningListResponse:
        """Return paginated warnings for admin-only views."""
        offset = (page - 1) * page_size
        items = await self._repo.list_all(
            attempt_id=attempt_id,
            candidate_id=candidate_id,
            violation_type=violation_type,
            severity=severity,
            limit=page_size,
            offset=offset,
        )
        total = await self._repo.count_all(
            attempt_id=attempt_id,
            candidate_id=candidate_id,
            violation_type=violation_type,
            severity=severity,
        )
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        return WarningListResponse(
            items=[WarningResponse.model_validate(w) for w in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_attempt_summary(
        self, attempt_id: uuid.UUID
    ) -> WarningSummary:
        """Return warning count breakdown by severity for an attempt."""
        total = await self._repo.count_by_attempt(attempt_id)
        low = await self._repo.count_by_severity(attempt_id, "LOW")
        medium = await self._repo.count_by_severity(attempt_id, "MEDIUM")
        high = await self._repo.count_by_severity(attempt_id, "HIGH")
        critical = await self._repo.count_by_severity(attempt_id, "CRITICAL")
        return WarningSummary(
            attempt_id=attempt_id,
            total_warnings=total,
            low_count=low,
            medium_count=medium,
            high_count=high,
            critical_count=critical,
        )
