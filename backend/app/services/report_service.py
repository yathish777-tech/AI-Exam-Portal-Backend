"""
app/services/report_service.py
================================
Business logic for report generation.

SECURITY NOTES:
- Exam reports: interviewers may only generate for their own exams.
- Candidate reports: ADMIN only (contains cross-exam data).
- All data is server-computed; no client-supplied scores accepted.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.exam import Exam
from app.models.exam_attempt import ExamAttempt
from app.models.exam_candidate import ExamCandidate
from app.models.exam_result import ExamResult
from app.models.proctoring_warning import ProctoringWarning
from app.models.user import User
from app.schemas.report import (
    CandidateReport,
    CandidateReportEntry,
    ExamReport,
    ExamReportEntry,
)


class ReportService:
    """Report generation for exams and candidates."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def generate_exam_report(
        self,
        exam_id: uuid.UUID,
        *,
        requesting_user_id: uuid.UUID,
        is_admin: bool = False,
    ) -> ExamReport:
        """
        Generate a full exam report with ranked candidate results.
        Interviewers may only generate reports for their own exams.
        """
        exam = await self._db.get(Exam, exam_id)
        if exam is None:
            raise NotFoundError("Exam not found.")
        if not is_admin and exam.created_by != requesting_user_id:
            raise AuthorizationError()

        # All candidates assigned
        total_candidates = (
            await self._db.execute(
                select(func.count()).where(ExamCandidate.exam_id == exam_id)
            )
        ).scalar_one()

        # All results with attempt and user data
        stmt = (
            select(ExamResult, ExamAttempt, User, ProctoringWarning.id)
            .join(ExamAttempt, ExamResult.attempt_id == ExamAttempt.id)
            .join(User, ExamResult.candidate_id == User.id)
            .outerjoin(
                ProctoringWarning,
                ProctoringWarning.attempt_id == ExamAttempt.id,
            )
            .where(ExamResult.exam_id == exam_id)
            .group_by(ExamResult.id, ExamAttempt.id, User.id)
            .order_by(ExamResult.score.desc(), ExamAttempt.submitted_at.asc())
        )
        rows = (await self._db.execute(stmt)).all()

        # Calculate warning counts per attempt
        warnings_by_attempt: dict[uuid.UUID, int] = {}
        warn_stmt = (
            select(ExamAttempt.id, func.count(ProctoringWarning.id))
            .join(ProctoringWarning, ProctoringWarning.attempt_id == ExamAttempt.id)
            .where(ExamAttempt.exam_id == exam_id)
            .group_by(ExamAttempt.id)
        )
        for attempt_id, warn_count in (await self._db.execute(warn_stmt)).all():
            warnings_by_attempt[attempt_id] = warn_count

        entries = []
        scores = []
        submitted_count = 0
        for rank, row in enumerate(rows, start=1):
            res, attempt, user, _ = row
            w_count = warnings_by_attempt.get(attempt.id, 0)
            pct = float(res.percentage)
            scores.append(pct)
            if attempt.status == "SUBMITTED":
                submitted_count += 1
            entries.append(
                ExamReportEntry(
                    rank=rank,
                    candidate_id=user.id,
                    email=user.email,
                    attempt_status=attempt.status,
                    score=float(res.score),
                    total_marks=float(res.total_marks),
                    percentage=pct,
                    correct_count=res.correct_count,
                    total_questions=res.total_questions,
                    result_status=res.status,
                    started_at=attempt.started_at,
                    submitted_at=attempt.submitted_at,
                    proctoring_warnings=w_count,
                )
            )

        avg_pct = round(sum(scores) / len(scores), 2) if scores else None
        pass_count = sum(1 for s in scores if s >= 50.0)
        fail_count = len(scores) - pass_count

        return ExamReport(
            exam_id=exam.id,
            exam_title=exam.title,
            exam_status=exam.status,
            duration_minutes=exam.duration_minutes,
            scheduled_at=exam.scheduled_at,
            created_at=exam.created_at,
            total_candidates=total_candidates,
            submitted_count=submitted_count,
            average_percentage=avg_pct,
            pass_count=pass_count,
            fail_count=fail_count,
            entries=entries,
            generated_at=datetime.now(timezone.utc),
        )

    async def generate_candidate_report(
        self, candidate_id: uuid.UUID
    ) -> CandidateReport:
        """Generate a full performance report for a candidate. ADMIN only."""
        user = await self._db.get(User, candidate_id)
        if user is None:
            raise NotFoundError("Candidate not found.")

        # All assigned exams
        assigned_stmt = select(ExamCandidate, Exam).join(
            Exam, ExamCandidate.exam_id == Exam.id
        ).where(ExamCandidate.candidate_id == candidate_id)
        assigned_rows = (await self._db.execute(assigned_stmt)).all()

        entries = []
        percentages = []
        submitted_count = 0

        for ec, exam in assigned_rows:
            # Get attempt and result
            attempt = (
                await self._db.execute(
                    select(ExamAttempt).where(
                        ExamAttempt.exam_id == exam.id,
                        ExamAttempt.candidate_id == candidate_id,
                    )
                )
            ).scalar_one_or_none()

            result = None
            if attempt:
                result = (
                    await self._db.execute(
                        select(ExamResult).where(ExamResult.attempt_id == attempt.id)
                    )
                ).scalar_one_or_none()

            warn_count = 0
            if attempt:
                warn_count = (
                    await self._db.execute(
                        select(func.count()).where(
                            ProctoringWarning.attempt_id == attempt.id
                        )
                    )
                ).scalar_one()

            if attempt and attempt.status == "SUBMITTED":
                submitted_count += 1
            if result:
                percentages.append(float(result.percentage))

            entries.append(
                CandidateReportEntry(
                    exam_id=exam.id,
                    exam_title=exam.title,
                    attempt_status=attempt.status if attempt else None,
                    score=float(result.score) if result else None,
                    total_marks=float(result.total_marks) if result else None,
                    percentage=float(result.percentage) if result else None,
                    result_status=result.status if result else None,
                    submitted_at=attempt.submitted_at if attempt else None,
                    proctoring_warnings=warn_count,
                )
            )

        avg_pct = round(sum(percentages) / len(percentages), 2) if percentages else None

        return CandidateReport(
            candidate_id=user.id,
            email=user.email,
            total_exams_assigned=len(assigned_rows),
            total_exams_submitted=submitted_count,
            average_percentage=avg_pct,
            entries=entries,
            generated_at=datetime.now(timezone.utc),
        )
