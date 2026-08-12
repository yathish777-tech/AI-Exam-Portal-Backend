"""
app/services/attempt_service.py
=================================
Business logic for starting and retrieving exam attempts.

SECURITY:
- ONE ATTEMPT PER CANDIDATE PER EXAM — enforced at both DB (UNIQUE constraint)
  and service layer.
- `candidate_id` is ALWAYS set from the authenticated user — never from the
  request body.
- Candidates can only access their own attempts (IDOR prevention).
- Exam must be PUBLISHED or SCHEDULED for a candidate to start it.
- Candidate must be assigned to the exam before starting.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AttemptStatus, ExamStatus, RoleName, SecurityEvent
from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError, ValidationError
from app.core.logging import log_security_event
from app.models.user import User
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.exam_attempt import AttemptResponse, AttemptStartResponse
from app.schemas.question import QuestionCandidateResponse


class AttemptService:
    """
    Orchestrates exam attempt lifecycle.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._attempts = AttemptRepository
        self._exams = ExamRepository
        self._questions = QuestionRepository
        self._candidates = CandidateRepository

    # -----------------------------------------------------------------------
    # Start attempt
    # -----------------------------------------------------------------------

    async def start_attempt(
        self,
        exam_id: uuid.UUID,
        current_user: User,
        *,
        request_id: str = "",
    ) -> AttemptStartResponse:
        """
        Start an exam attempt for the authenticated candidate.

        Business rules:
        1. Exam must exist and be PUBLISHED or SCHEDULED.
        2. Candidate must be assigned to the exam.
        3. ONE attempt per candidate per exam — duplicate raises ConflictError.
        4. Returns the attempt with all questions (correct_index stripped).

        SECURITY: `candidate_id` is always `current_user.id` — never from body.
        """
        # 1. Fetch the exam
        exam = await self._exams.get_by_id_with_owner_check(
            self._db, exam_id, owner_id=None  # No owner filter for candidates
        )
        if exam is None:
            raise NotFoundError(f"Exam {exam_id} not found.")

        # 2. Exam must be in a startable status
        if exam.status not in (
            ExamStatus.PUBLISHED, ExamStatus.PUBLISHED.value,
            ExamStatus.SCHEDULED, ExamStatus.SCHEDULED.value,
        ):
            raise ValidationError(
                f"Exam is not available for attempts (status: {exam.status})."
            )

        if exam.status in (ExamStatus.SCHEDULED, ExamStatus.SCHEDULED.value):
            scheduled_at = exam.scheduled_at
            if scheduled_at is None:
                raise ValidationError("Scheduled exam has no start time configured.")
            if scheduled_at.tzinfo is None:
                scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
            if scheduled_at > datetime.now(timezone.utc):
                raise ValidationError("Exam is scheduled for a future time.")

        # 3. Candidate must be assigned
        is_assigned = await self._candidates.is_assigned(
            self._db, exam_id, current_user.id
        )
        if not is_assigned:
            log_security_event(
                SecurityEvent.IDOR_ATTEMPT,
                request_id=request_id,
                user_id=str(current_user.id),
                ip_address="",
                endpoint=f"/exams/{exam_id}/start",
                success=False,
                detail="Candidate not assigned to exam",
            )
            raise NotFoundError(f"Exam {exam_id} not found.")

        # 4. Check for existing attempt (one per candidate per exam)
        existing = await self._attempts.get_by_exam_and_candidate(
            self._db, exam_id, current_user.id
        )
        if existing is not None:
            if existing.status == AttemptStatus.SUBMITTED:
                log_security_event(
                    SecurityEvent.EXAM_ALREADY_SUBMITTED,
                    request_id=request_id,
                    user_id=str(current_user.id),
                    ip_address="",
                    endpoint=f"/exams/{exam_id}/start",
                    success=False,
                )
                raise ConflictError(
                    "You have already submitted this exam. "
                    "Multiple attempts are not allowed."
                )
            # IN_PROGRESS — return existing attempt (resume)
            questions = await self._questions.list_by_exam(self._db, exam_id)
            attempt_response = AttemptResponse(
                id=existing.id,
                exam_id=existing.exam_id,
                candidate_id=existing.candidate_id,
                status=existing.status,
                started_at=existing.started_at,
                submitted_at=existing.submitted_at,
                questions=[QuestionCandidateResponse.from_question(q) for q in questions],
                duration_minutes=exam.duration_minutes,
                exam_title=exam.title,
            )
            return AttemptStartResponse(
                attempt=attempt_response,
                message="Resuming your in-progress exam attempt.",
            )

        # 5. Create new attempt
        from app.models.exam_attempt import ExamAttempt

        attempt = ExamAttempt(
            exam_id=exam_id,
            candidate_id=current_user.id,  # ALWAYS from authenticated user
            status=AttemptStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
        )
        try:
            db_attempt = await self._attempts.save(self._db, attempt)
            await self._db.commit()
            await self._db.refresh(db_attempt)
        except IntegrityError:
            await self._db.rollback()
            log_security_event(
                SecurityEvent.ATTEMPT_DUPLICATE,
                request_id=request_id,
                user_id=str(current_user.id),
                ip_address="",
                endpoint=f"/exams/{exam_id}/start",
                success=False,
                detail="Race condition: duplicate attempt detected",
            )
            raise ConflictError(
                "An attempt for this exam already exists. "
                "Concurrent attempts are not allowed."
            )

        # 6. Fetch questions (with correct_index stripped for candidate)
        questions = await self._questions.list_by_exam(self._db, exam_id)

        log_security_event(
            SecurityEvent.ATTEMPT_STARTED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/exams/{exam_id}/start",
        )

        attempt_response = AttemptResponse(
            id=db_attempt.id,
            exam_id=db_attempt.exam_id,
            candidate_id=db_attempt.candidate_id,
            status=db_attempt.status,
            started_at=db_attempt.started_at,
            submitted_at=db_attempt.submitted_at,
            questions=[QuestionCandidateResponse.from_question(q) for q in questions],
            duration_minutes=exam.duration_minutes,
            exam_title=exam.title,
        )
        return AttemptStartResponse(
            attempt=attempt_response,
            message="Exam attempt started successfully.",
        )

    # -----------------------------------------------------------------------
    # Get attempt
    # -----------------------------------------------------------------------

    async def get_attempt(
        self,
        attempt_id: uuid.UUID,
        current_user: User,
    ) -> AttemptResponse:
        """
        Return attempt details for the authenticated user.

        - CANDIDATE: can only see their own attempt.
        - ADMIN/INTERVIEWER: can see any attempt for their exams.
        """
        user_role = current_user.role.name if current_user.role else ""

        if user_role == RoleName.CANDIDATE:
            attempt = await self._attempts.get_by_id_for_candidate(
                self._db, attempt_id, current_user.id
            )
            if attempt is None:
                raise NotFoundError(f"Attempt {attempt_id} not found.")

            exam = await self._exams.get_by_id_with_owner_check(
                self._db, attempt.exam_id, owner_id=None
            )
            questions = await self._questions.list_by_exam(self._db, attempt.exam_id)
            return AttemptResponse(
                id=attempt.id,
                exam_id=attempt.exam_id,
                candidate_id=attempt.candidate_id,
                status=attempt.status,
                started_at=attempt.started_at,
                submitted_at=attempt.submitted_at,
                questions=[QuestionCandidateResponse.from_question(q) for q in questions],
                duration_minutes=exam.duration_minutes if exam else None,
                exam_title=exam.title if exam else "",
            )
        else:
            # Admin/Interviewer — fetch attempt and verify exam ownership
            attempt = await self._attempts.get_by_id(self._db, attempt_id)
            if attempt is None:
                raise NotFoundError(f"Attempt {attempt_id} not found.")

            # Verify exam belongs to this interviewer (or admin bypass)
            if user_role == RoleName.INTERVIEWER:
                exam = await self._exams.get_by_id_with_owner_check(
                    self._db, attempt.exam_id, owner_id=current_user.id
                )
                if exam is None:
                    raise NotFoundError(f"Attempt {attempt_id} not found.")
            else:
                exam = await self._exams.get_by_id_with_owner_check(
                    self._db, attempt.exam_id, owner_id=None
                )

            return AttemptResponse(
                id=attempt.id,
                exam_id=attempt.exam_id,
                candidate_id=attempt.candidate_id,
                status=attempt.status,
                started_at=attempt.started_at,
                submitted_at=attempt.submitted_at,
                questions=[],  # Not needed for admin/interviewer view
                duration_minutes=exam.duration_minutes if exam else None,
                exam_title=exam.title if exam else "",
            )
