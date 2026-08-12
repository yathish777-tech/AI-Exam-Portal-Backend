"""
app/services/analytics_service.py
=====================================
Business logic for analytics/dashboard statistics.

SECURITY NOTES:
- Platform stats are ADMIN only (enforced at router).
- Exam analytics are scoped to the requesting interviewer's exams
  (or unrestricted for ADMIN).
- No candidate PII is leaked — only aggregated stats.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ExamStatus, RoleName
from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.exam import Exam
from app.models.exam_attempt import ExamAttempt
from app.models.exam_candidate import ExamCandidate
from app.models.exam_result import ExamResult
from app.models.proctoring_warning import ProctoringWarning
from app.models.role import Role
from app.models.user import User
from app.schemas.analytics import CandidateAnalytics, ExamAnalytics, PlatformStats


class AnalyticsService:
    """Platform and exam analytics."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_platform_stats(self) -> PlatformStats:
        """Return high-level platform statistics. ADMIN only."""

        async def count(model, *conditions):
            stmt = select(func.count()).select_from(model)
            for cond in conditions:
                stmt = stmt.where(cond)
            return (await self._db.execute(stmt)).scalar_one()

        async def count_role(role_name: str) -> int:
            return (
                await self._db.execute(
                    select(func.count())
                    .select_from(User)
                    .join(Role, User.role_id == Role.id)
                    .where(Role.name == role_name)
                )
            ).scalar_one()

        total_users = await count(User)
        total_admins = await count_role(RoleName.ADMIN)
        total_interviewers = await count_role(RoleName.INTERVIEWER)
        total_candidates = await count_role(RoleName.CANDIDATE)
        active_users = await count(User, User.is_active == True)
        inactive_users = total_users - active_users

        total_exams = await count(Exam)
        draft_exams = await count(Exam, Exam.status == ExamStatus.DRAFT)
        published_exams = await count(Exam, Exam.status == ExamStatus.PUBLISHED)
        completed_exams = await count(Exam, Exam.status == ExamStatus.COMPLETED)

        total_attempts = await count(ExamAttempt)
        submitted_attempts = await count(ExamAttempt, ExamAttempt.status == "SUBMITTED")
        in_progress_attempts = await count(ExamAttempt, ExamAttempt.status == "IN_PROGRESS")

        total_results = await count(ExamResult)
        evaluated_results = await count(ExamResult, ExamResult.status == "EVALUATED")
        pending_evaluation_results = await count(ExamResult, ExamResult.status == "PENDING_EVALUATION")

        total_warnings = await count(ProctoringWarning)

        return PlatformStats(
            total_users=total_users,
            total_admins=total_admins,
            total_interviewers=total_interviewers,
            total_candidates=total_candidates,
            active_users=active_users,
            inactive_users=inactive_users,
            total_exams=total_exams,
            draft_exams=draft_exams,
            published_exams=published_exams,
            completed_exams=completed_exams,
            total_attempts=total_attempts,
            submitted_attempts=submitted_attempts,
            in_progress_attempts=in_progress_attempts,
            total_results=total_results,
            evaluated_results=evaluated_results,
            pending_evaluation_results=pending_evaluation_results,
            total_proctoring_warnings=total_warnings,
        )

    async def get_exam_analytics(
        self,
        exam_id: uuid.UUID,
        *,
        requesting_user_id: uuid.UUID,
        is_admin: bool = False,
    ) -> ExamAnalytics:
        """
        Return analytics for a specific exam.
        Interviewers may only see their own exams.
        """
        exam = await self._db.get(Exam, exam_id)
        if exam is None:
            raise NotFoundError("Exam not found.")
        if not is_admin and exam.created_by != requesting_user_id:
            raise AuthorizationError()

        async def count(model, *conditions):
            stmt = select(func.count()).select_from(model)
            for cond in conditions:
                stmt = stmt.where(cond)
            return (await self._db.execute(stmt)).scalar_one()

        total_candidates = await count(ExamCandidate, ExamCandidate.exam_id == exam_id)
        started = await count(ExamAttempt, ExamAttempt.exam_id == exam_id)
        submitted = await count(
            ExamAttempt,
            ExamAttempt.exam_id == exam_id,
            ExamAttempt.status == "SUBMITTED",
        )
        abandoned = await count(
            ExamAttempt,
            ExamAttempt.exam_id == exam_id,
            ExamAttempt.status == "ABANDONED",
        )
        completion_rate = (
            round(submitted / total_candidates * 100, 2)
            if total_candidates > 0
            else 0.0
        )

        # Score aggregates
        score_stmt = select(
            func.avg(ExamResult.score),
            func.max(ExamResult.score),
            func.min(ExamResult.score),
            func.avg(ExamResult.percentage),
        ).where(ExamResult.exam_id == exam_id)
        score_row = (await self._db.execute(score_stmt)).one()
        avg_score = float(score_row[0]) if score_row[0] else None
        max_score = float(score_row[1]) if score_row[1] else None
        min_score = float(score_row[2]) if score_row[2] else None
        avg_pct = float(score_row[3]) if score_row[3] else None

        evaluated = await count(ExamResult, ExamResult.exam_id == exam_id, ExamResult.status == "EVALUATED")
        pending = await count(ExamResult, ExamResult.exam_id == exam_id, ExamResult.status == "PENDING_EVALUATION")

        warnings = (
            await self._db.execute(
                select(func.count())
                .select_from(ProctoringWarning)
                .join(ExamAttempt, ProctoringWarning.attempt_id == ExamAttempt.id)
                .where(ExamAttempt.exam_id == exam_id)
            )
        ).scalar_one()

        return ExamAnalytics(
            exam_id=exam.id,
            exam_title=exam.title,
            exam_status=exam.status,
            total_candidates=total_candidates,
            started_attempts=started,
            submitted_attempts=submitted,
            abandoned_attempts=abandoned,
            completion_rate=completion_rate,
            average_score=avg_score,
            highest_score=max_score,
            lowest_score=min_score,
            average_percentage=avg_pct,
            evaluated_results=evaluated,
            pending_evaluation_results=pending,
            total_proctoring_warnings=warnings,
        )

    async def get_candidate_analytics(
        self, candidate_id: uuid.UUID
    ) -> CandidateAnalytics:
        """Return analytics for a specific candidate. ADMIN only."""
        user = await self._db.get(User, candidate_id)
        if user is None:
            raise NotFoundError("Candidate not found.")

        async def count(model, *conditions):
            stmt = select(func.count()).select_from(model)
            for cond in conditions:
                stmt = stmt.where(cond)
            return (await self._db.execute(stmt)).scalar_one()

        assigned = await count(ExamCandidate, ExamCandidate.candidate_id == candidate_id)
        attempted = await count(ExamAttempt, ExamAttempt.candidate_id == candidate_id)
        submitted = await count(
            ExamAttempt,
            ExamAttempt.candidate_id == candidate_id,
            ExamAttempt.status == "SUBMITTED",
        )

        score_stmt = select(
            func.avg(ExamResult.score),
            func.avg(ExamResult.percentage),
            func.max(ExamResult.percentage),
        ).where(ExamResult.candidate_id == candidate_id)
        score_row = (await self._db.execute(score_stmt)).one()

        warnings_total = await count(
            ProctoringWarning, ProctoringWarning.candidate_id == candidate_id
        )
        warnings_high = await count(
            ProctoringWarning,
            ProctoringWarning.candidate_id == candidate_id,
            ProctoringWarning.severity.in_(["HIGH", "CRITICAL"]),
        )

        return CandidateAnalytics(
            candidate_id=candidate_id,
            email=user.email,
            total_exams_assigned=assigned,
            total_exams_attempted=attempted,
            total_exams_submitted=submitted,
            average_score=float(score_row[0]) if score_row[0] else None,
            average_percentage=float(score_row[1]) if score_row[1] else None,
            highest_percentage=float(score_row[2]) if score_row[2] else None,
            total_proctoring_warnings=warnings_total,
            high_severity_warnings=warnings_high,
        )
