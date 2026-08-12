"""
app/services/student_service.py
==================================
Business logic for Student (CANDIDATE) dashboard endpoints.

SECURITY NOTES:
- All operations are scoped to the authenticated candidate's user_id.
- candidate_id is NEVER accepted from request body — always from JWT.
- IDOR is prevented by filtering all queries on candidate_id.
"""

from __future__ import annotations

import uuid
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import RoleName
from app.core.exceptions import NotFoundError
from app.models.exam import Exam
from app.models.exam_attempt import ExamAttempt
from app.models.exam_candidate import ExamCandidate
from app.models.exam_result import ExamResult
from app.repositories.result_repository import ResultRepository
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.student import (
    StudentExamListResponse,
    StudentExamSummary,
    StudentProfileResponse,
    StudentResultListResponse,
    StudentResultSummary,
)
from app.services.user_service import UserService


class StudentService:
    """Student (candidate) dashboard operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._result_repo = ResultRepository(db)
        self._user_service = UserService(db)

    async def get_profile(self, candidate_id: uuid.UUID) -> StudentProfileResponse:
        """Return the candidate's own profile."""
        user = await self._user_service.get_by_id(candidate_id)
        return StudentProfileResponse(
            id=user.id,
            email=user.email,
            role=user.role.name if user.role else "CANDIDATE",
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )

    async def list_assigned_exams(
        self,
        candidate_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> StudentExamListResponse:
        """
        Return paginated exams assigned to this candidate.
        Includes attempt status if an attempt exists.
        IDOR guard: always filter on candidate_id.
        """
        offset = (page - 1) * page_size

        # Count total assigned
        count_stmt = select(func.count()).where(
            ExamCandidate.candidate_id == candidate_id
        )
        total_result = await self._db.execute(count_stmt)
        total = total_result.scalar_one()

        # Fetch assigned exams with exam data
        stmt = (
            select(ExamCandidate, Exam, ExamAttempt)
            .join(Exam, ExamCandidate.exam_id == Exam.id)
            .outerjoin(
                ExamAttempt,
                (ExamAttempt.exam_id == Exam.id)
                & (ExamAttempt.candidate_id == candidate_id),
            )
            .where(ExamCandidate.candidate_id == candidate_id)
            .order_by(ExamCandidate.assigned_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        result = await self._db.execute(stmt)
        rows = result.all()

        items = []
        for ec, exam, attempt in rows:
            items.append(
                StudentExamSummary(
                    exam_id=exam.id,
                    title=exam.title,
                    description=exam.description,
                    duration_minutes=exam.duration_minutes,
                    status=exam.status,
                    scheduled_at=exam.scheduled_at,
                    assigned_at=ec.assigned_at,
                    attempt_id=attempt.id if attempt else None,
                    attempt_status=attempt.status if attempt else None,
                    started_at=attempt.started_at if attempt else None,
                    submitted_at=attempt.submitted_at if attempt else None,
                )
            )

        total_pages = ceil(total / page_size) if page_size > 0 else 0
        return StudentExamListResponse(
            items=items, total=total, page=page, page_size=page_size,
            total_pages=total_pages,
        )

    async def list_results(
        self,
        candidate_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> StudentResultListResponse:
        """
        Return paginated exam results for this candidate.
        IDOR guard: all results scoped to candidate_id.
        """
        offset = (page - 1) * page_size

        count_stmt = select(func.count()).where(
            ExamResult.candidate_id == candidate_id
        )
        total_result = await self._db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = (
            select(ExamResult, Exam, ExamAttempt)
            .join(Exam, ExamResult.exam_id == Exam.id)
            .join(ExamAttempt, ExamResult.attempt_id == ExamAttempt.id)
            .where(ExamResult.candidate_id == candidate_id)
            .order_by(ExamResult.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        result = await self._db.execute(stmt)
        rows = result.all()

        items = []
        for res, exam, attempt in rows:
            items.append(
                StudentResultSummary(
                    result_id=res.id,
                    exam_id=exam.id,
                    exam_title=exam.title,
                    attempt_id=attempt.id,
                    score=float(res.score),
                    total_marks=float(res.total_marks),
                    percentage=float(res.percentage),
                    total_questions=res.total_questions,
                    attempted_count=res.attempted_count,
                    correct_count=res.correct_count,
                    status=res.status,
                    submitted_at=attempt.submitted_at,
                    created_at=res.created_at,
                )
            )

        total_pages = ceil(total / page_size) if page_size > 0 else 0
        return StudentResultListResponse(
            items=items, total=total, page=page, page_size=page_size,
            total_pages=total_pages,
        )

    async def get_result(
        self, candidate_id: uuid.UUID, result_id: uuid.UUID
    ) -> StudentResultSummary:
        """Return one result owned by the authenticated candidate."""
        stmt = (
            select(ExamResult, Exam, ExamAttempt)
            .join(Exam, ExamResult.exam_id == Exam.id)
            .join(ExamAttempt, ExamResult.attempt_id == ExamAttempt.id)
            .where(ExamResult.id == result_id, ExamResult.candidate_id == candidate_id)
        )
        row = (await self._db.execute(stmt)).one_or_none()
        if row is None:
            raise NotFoundError("Result not found.")
        res, exam, attempt = row
        return StudentResultSummary(
            result_id=res.id,
            exam_id=exam.id,
            exam_title=exam.title,
            attempt_id=attempt.id,
            score=float(res.score),
            total_marks=float(res.total_marks),
            percentage=float(res.percentage),
            total_questions=res.total_questions,
            attempted_count=res.attempted_count,
            correct_count=res.correct_count,
            status=res.status,
            submitted_at=attempt.submitted_at,
            created_at=res.created_at,
        )
