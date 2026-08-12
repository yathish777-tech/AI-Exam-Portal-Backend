"""
app/services/result_service.py
================================
Business logic for retrieving exam results.

SECURITY:
- Candidates can only access their own result (IDOR prevention).
- Interviewers can only access results for their own exams.
- Admins can access any result.
- Results are read-only — no modification allowed via this service.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import RoleName
from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.user import User
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.submission_repository import SubmissionRepository
from app.schemas.result import ExamResultsListResponse, ResultResponse, ResultSummaryItem
from app.schemas.submission import SubmissionItemResponse


class ResultService:
    """
    Orchestrates result retrieval with role-based visibility.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._results = ResultRepository
        self._attempts = AttemptRepository
        self._exams = ExamRepository
        self._submissions = SubmissionRepository

    # -----------------------------------------------------------------------
    # Get result for an attempt
    # -----------------------------------------------------------------------

    async def get_attempt_result(
        self,
        attempt_id: uuid.UUID,
        current_user: User,
        include_answers: bool = False,
    ) -> ResultResponse:
        """
        Return the result for a specific attempt.

        - CANDIDATE: can only see their own result. Attempt must be SUBMITTED.
        - INTERVIEWER: can see results for their exam's attempts.
        - ADMIN: can see any result.

        Args:
            include_answers: If True, include per-question answer breakdown.
                             Only returned after submission.
        """
        user_role = current_user.role.name if current_user.role else ""

        if user_role == RoleName.CANDIDATE:
            # Candidate: verify they own the attempt
            attempt = await self._attempts.get_by_id_for_candidate(
                self._db, attempt_id, current_user.id
            )
            if attempt is None:
                raise NotFoundError(f"Attempt {attempt_id} not found.")

            result = await self._results.get_by_attempt_for_candidate(
                self._db, attempt_id, current_user.id
            )
            if result is None:
                raise NotFoundError(
                    "Result not available yet. Submit the exam first."
                )

        elif user_role == RoleName.INTERVIEWER:
            # Interviewer: verify the attempt's exam is theirs
            attempt = await self._attempts.get_by_id(self._db, attempt_id)
            if attempt is None:
                raise NotFoundError(f"Attempt {attempt_id} not found.")

            exam = await self._exams.get_by_id_with_owner_check(
                self._db, attempt.exam_id, owner_id=current_user.id
            )
            if exam is None:
                raise NotFoundError(f"Attempt {attempt_id} not found.")

            result = await self._results.get_by_attempt_id(self._db, attempt_id)
            if result is None:
                raise NotFoundError("Result not found for this attempt.")

        else:
            # Admin: no ownership check
            result = await self._results.get_by_attempt_id(self._db, attempt_id)
            if result is None:
                raise NotFoundError(f"Result for attempt {attempt_id} not found.")

        # Build answer breakdown if requested
        answers: list[SubmissionItemResponse] = []
        if include_answers:
            subs = await self._submissions.list_by_attempt(self._db, attempt_id)
            answers = [SubmissionItemResponse.model_validate(s) for s in subs]

        return ResultResponse(
            id=result.id,
            attempt_id=result.attempt_id,
            candidate_id=result.candidate_id,
            exam_id=result.exam_id,
            total_questions=result.total_questions,
            attempted_count=result.attempted_count,
            correct_count=result.correct_count,
            incorrect_count=result.incorrect_count,
            total_marks=float(result.total_marks),
            score=float(result.score),
            percentage=float(result.percentage),
            status=result.status,
            created_at=result.created_at,
            updated_at=result.updated_at,
            answers=answers,
        )

    # -----------------------------------------------------------------------
    # List results for an exam
    # -----------------------------------------------------------------------

    async def list_exam_results(
        self,
        exam_id: uuid.UUID,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> ExamResultsListResponse:
        """
        Return paginated results for all candidates in an exam.

        - INTERVIEWER: only for their own exams.
        - ADMIN: any exam.
        - CANDIDATE: access denied (use get_attempt_result instead).
        """
        user_role = current_user.role.name if current_user.role else ""

        # Verify exam exists and is accessible
        owner_id = None if user_role == RoleName.ADMIN else current_user.id
        exam = await self._exams.get_by_id_with_owner_check(
            self._db, exam_id, owner_id=owner_id
        )
        if exam is None:
            raise NotFoundError(f"Exam {exam_id} not found.")

        rows, total = await self._results.list_by_exam(
            self._db, exam_id, skip=skip, limit=limit
        )

        items = [
            ResultSummaryItem(
                id=row["result"].id,
                attempt_id=row["result"].attempt_id,
                candidate_id=row["result"].candidate_id,
                candidate_email=row["candidate_email"],
                total_marks=float(row["result"].total_marks),
                score=float(row["result"].score),
                percentage=float(row["result"].percentage),
                status=row["result"].status,
                created_at=row["result"].created_at,
            )
            for row in rows
        ]

        return ExamResultsListResponse(
            items=items,
            total=total,
            exam_id=exam_id,
        )
