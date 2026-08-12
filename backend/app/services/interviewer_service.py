"""
app/services/interviewer_service.py
=====================================
Business logic for Interviewer dashboard endpoints.

SECURITY NOTES:
- Interviewers can only see exams they created (enforced by created_by filter).
- Candidate data is only visible for exams the interviewer owns.
- Leaderboard scores are server-computed — never from client.
- ADMIN users can also access this service for oversight.
"""

from __future__ import annotations

import uuid
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam import Exam
from app.models.exam_attempt import ExamAttempt
from app.models.exam_candidate import ExamCandidate
from app.models.exam_result import ExamResult
from app.models.question import Question
from app.repositories.log_repository import LogRepository
from app.models.user import User
from app.schemas.interviewer import (
    InterviewerCandidateEntry,
    InterviewerCandidateListResponse,
    InterviewerExamListResponse,
    InterviewerExamSummary,
    InterviewerProfileResponse,
    LeaderboardEntry,
    LeaderboardResponse,
)
from app.services.user_service import UserService
from app.core.exceptions import AuthorizationError, NotFoundError


class InterviewerService:
    """Interviewer dashboard operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._user_service = UserService(db)
        self._log_repo = LogRepository(db)

    async def get_profile(self, interviewer_id: uuid.UUID) -> InterviewerProfileResponse:
        """Return the interviewer's own profile."""
        user = await self._user_service.get_by_id(interviewer_id)
        return InterviewerProfileResponse(
            id=user.id,
            email=user.email,
            role=user.role.name if user.role else "INTERVIEWER",
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )

    async def list_my_exams(
        self,
        interviewer_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> InterviewerExamListResponse:
        """
        Return paginated exams created by this interviewer with stats.
        IDOR: always filter on created_by == interviewer_id.
        """
        offset = (page - 1) * page_size

        count_stmt = select(func.count()).where(Exam.created_by == interviewer_id)
        total = (await self._db.execute(count_stmt)).scalar_one()

        stmt = (
            select(Exam)
            .where(Exam.created_by == interviewer_id)
            .order_by(Exam.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        result = await self._db.execute(stmt)
        exams = list(result.scalars().all())

        items = []
        for exam in exams:
            q_count = (
                await self._db.execute(
                    select(func.count()).where(Question.exam_id == exam.id)
                )
            ).scalar_one()
            c_count = (
                await self._db.execute(
                    select(func.count()).where(ExamCandidate.exam_id == exam.id)
                )
            ).scalar_one()
            s_count = (
                await self._db.execute(
                    select(func.count()).where(
                        ExamAttempt.exam_id == exam.id,
                        ExamAttempt.status == "SUBMITTED",
                    )
                )
            ).scalar_one()
            items.append(
                InterviewerExamSummary(
                    id=exam.id,
                    title=exam.title,
                    description=exam.description,
                    status=exam.status,
                    duration_minutes=exam.duration_minutes,
                    scheduled_at=exam.scheduled_at,
                    created_at=exam.created_at,
                    total_questions=q_count,
                    total_candidates=c_count,
                    total_submissions=s_count,
                )
            )

        total_pages = ceil(total / page_size) if page_size > 0 else 0
        return InterviewerExamListResponse(
            items=items, total=total, page=page, page_size=page_size,
            total_pages=total_pages,
        )

    async def list_my_candidates(
        self,
        interviewer_id: uuid.UUID,
        *,
        exam_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> InterviewerCandidateListResponse:
        """
        Return candidates for the interviewer's exams.
        If exam_id provided, filter to that exam (must belong to interviewer).
        """
        offset = (page - 1) * page_size

        # Validate exam ownership when exam_id provided
        if exam_id is not None:
            exam = await self._db.get(Exam, exam_id)
            if exam is None:
                raise NotFoundError("Exam not found.")
            if exam.created_by != interviewer_id:
                raise AuthorizationError()

        stmt = (
            select(ExamCandidate, Exam, User, ExamAttempt, ExamResult)
            .join(Exam, ExamCandidate.exam_id == Exam.id)
            .join(User, ExamCandidate.candidate_id == User.id)
            .outerjoin(
                ExamAttempt,
                (ExamAttempt.exam_id == Exam.id)
                & (ExamAttempt.candidate_id == ExamCandidate.candidate_id),
            )
            .outerjoin(ExamResult, ExamResult.attempt_id == ExamAttempt.id)
            .where(Exam.created_by == interviewer_id)
        )
        if exam_id is not None:
            stmt = stmt.where(ExamCandidate.exam_id == exam_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._db.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(ExamCandidate.assigned_at.desc()).limit(page_size).offset(offset)
        rows = (await self._db.execute(stmt)).all()

        items = []
        for ec, exam, user, attempt, res in rows:
            items.append(
                InterviewerCandidateEntry(
                    candidate_id=user.id,
                    email=user.email,
                    exam_id=exam.id,
                    exam_title=exam.title,
                    assigned_at=ec.assigned_at,
                    attempt_status=attempt.status if attempt else None,
                    submitted_at=attempt.submitted_at if attempt else None,
                    score=float(res.score) if res else None,
                    percentage=float(res.percentage) if res else None,
                    result_status=res.status if res else None,
                )
            )

        total_pages = ceil(total / page_size) if page_size > 0 else 0
        return InterviewerCandidateListResponse(
            items=items, total=total, page=page, page_size=page_size,
            total_pages=total_pages,
        )

    async def get_leaderboard(
        self,
        exam_id: uuid.UUID,
        interviewer_id: uuid.UUID,
    ) -> LeaderboardResponse:
        """
        Return ranked leaderboard for an exam.
        Validates the exam belongs to the interviewer.
        """
        exam = await self._db.get(Exam, exam_id)
        if exam is None:
            raise NotFoundError("Exam not found.")
        if exam.created_by != interviewer_id:
            raise AuthorizationError()

        # Fetch all submitted results ordered by score desc
        stmt = (
            select(ExamResult, User, ExamAttempt)
            .join(User, ExamResult.candidate_id == User.id)
            .join(ExamAttempt, ExamResult.attempt_id == ExamAttempt.id)
            .where(ExamResult.exam_id == exam_id)
            .order_by(ExamResult.score.desc(), ExamAttempt.submitted_at.asc())
        )
        rows = (await self._db.execute(stmt)).all()

        entries = []
        for rank, (res, user, attempt) in enumerate(rows, start=1):
            entries.append(
                LeaderboardEntry(
                    rank=rank,
                    candidate_id=user.id,
                    email=user.email,
                    score=float(res.score),
                    total_marks=float(res.total_marks),
                    percentage=float(res.percentage),
                    correct_count=res.correct_count,
                    total_questions=res.total_questions,
                    submitted_at=attempt.submitted_at,
                )
            )

        return LeaderboardResponse(
            exam_id=exam.id,
            exam_title=exam.title,
            entries=entries,
            total_candidates=len(entries),
        )

    async def verify_exam_owner(
        self, exam_id: uuid.UUID, interviewer_id: uuid.UUID
    ) -> Exam:
        """Return an exam only when it belongs to the interviewer."""
        exam = await self._db.get(Exam, exam_id)
        if exam is None:
            raise NotFoundError("Exam not found.")
        if exam.created_by != interviewer_id:
            raise AuthorizationError()
        return exam

    async def verify_attempt_owner(
        self, attempt_id: uuid.UUID, interviewer_id: uuid.UUID
    ) -> ExamAttempt:
        """Return an attempt only when its exam belongs to the interviewer."""
        attempt = await self._db.get(ExamAttempt, attempt_id)
        if attempt is None:
            raise NotFoundError("Attempt not found.")
        await self.verify_exam_owner(attempt.exam_id, interviewer_id)
        return attempt

    async def list_attempt_activity(
        self,
        attempt_id: uuid.UUID,
        interviewer_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 50,
    ):
        """Return activity log entries for an owned attempt."""
        await self.verify_attempt_owner(attempt_id, interviewer_id)
        offset = (page - 1) * page_size
        items = await self._log_repo.list_all(
            resource_type="attempt", limit=page_size, offset=offset
        )
        items = [item for item in items if item.resource_id == attempt_id]
        total = len(items)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": 1 if total else 0,
        }

    async def publish_results(
        self, exam_id: uuid.UUID, interviewer_id: uuid.UUID
    ) -> dict[str, int | str]:
        """Mark result publication intent for an owned exam."""
        await self.verify_exam_owner(exam_id, interviewer_id)
        result = await self._db.execute(
            select(func.count()).where(ExamResult.exam_id == exam_id)
        )
        count = result.scalar_one()
        return {"message": "Results published.", "published_count": count}
