"""
app/services/question_service.py
===================================
Business logic for question management within exams.

SECURITY:
- Interviewers can only manage questions on their own exams.
- Admins can manage any exam's questions.
- MCQ `correct_index` is stored server-side; candidates never receive it.
- `exam_id` is always verified against the authenticated owner.
- Candidates cannot call any write operations (enforced at router).
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ExamStatus, QuestionType, RoleName, SecurityEvent
from app.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from app.core.logging import log_security_event
from app.models.user import User
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import (
    QuestionCreate,
    QuestionCandidateResponse,
    QuestionResponse,
    QuestionUpdate,
)


class QuestionService:
    """
    Orchestrates question CRUD operations scoped to exam ownership.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._questions = QuestionRepository
        self._exams = ExamRepository

    # -----------------------------------------------------------------------
    # Create
    # -----------------------------------------------------------------------

    async def create_question(
        self,
        exam_id: uuid.UUID,
        request: QuestionCreate,
        current_user: User,
        *,
        request_id: str = "",
    ) -> QuestionResponse:
        """
        Add a question to an exam.

        Validates:
        - Exam ownership.
        - Exam must be in DRAFT status (cannot add questions to published exams).
        - MCQ `options` structure (via schema validator).
        - Auto-assigns order_number if not provided.
        """
        exam = await self._get_owned_exam(exam_id, current_user)
        if exam.status not in (ExamStatus.DRAFT, ExamStatus.DRAFT.value):
            raise ValidationError(
                f"Cannot add questions to a {exam.status} exam. "
                "The exam must be in DRAFT status."
            )

        # Auto-assign order_number if not provided
        order_number = request.order_number
        if order_number is None:
            max_order = await self._questions.get_max_order_number(self._db, exam_id)
            order_number = max_order + 1

        from app.models.question import Question

        question = Question(
            exam_id=exam_id,
            question_type=request.question_type.value,
            content=request.content,
            marks=request.marks,
            order_number=order_number,
            options=request.options,
        )

        saved = await self._questions.save(self._db, question)
        await self._db.commit()
        await self._db.refresh(saved)

        log_security_event(
            SecurityEvent.QUESTION_CREATED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/exams/{exam_id}/questions",
        )

        return QuestionResponse.model_validate(saved)

    # -----------------------------------------------------------------------
    # Read
    # -----------------------------------------------------------------------

    async def list_questions(
        self,
        exam_id: uuid.UUID,
        current_user: User,
    ) -> list[QuestionResponse] | list[QuestionCandidateResponse]:
        """
        List questions for an exam.

        - ADMIN/INTERVIEWER: receive full QuestionResponse (includes correct_index).
        - CANDIDATE: receive QuestionCandidateResponse (correct_index stripped).

        SECURITY: Candidates only see questions on exams they are assigned to.
        """
        user_role = current_user.role.name if current_user.role else ""

        if user_role == RoleName.CANDIDATE:
            # Verify candidate is assigned to this exam
            await self._verify_candidate_assigned(exam_id, current_user.id)
            questions = await self._questions.list_by_exam(self._db, exam_id)
            return [QuestionCandidateResponse.from_question(q) for q in questions]
        else:
            # Verify ownership for interviewers
            await self._get_owned_exam(exam_id, current_user)
            questions = await self._questions.list_by_exam(self._db, exam_id)
            return [QuestionResponse.model_validate(q) for q in questions]

    async def get_question(
        self,
        question_id: uuid.UUID,
        current_user: User,
    ) -> QuestionResponse:
        """
        Get a single question by ID.

        Verifies the question's exam is accessible by the user.
        SECURITY: Candidates cannot use this endpoint (enforced at router).
        """
        from sqlalchemy import select
        from app.models.question import Question

        # Fetch the question first to get its exam_id
        stmt = select(Question).where(Question.id == question_id)
        result = await self._db.execute(stmt)
        question = result.scalar_one_or_none()

        if question is None:
            raise NotFoundError(f"Question {question_id} not found.")

        # Verify exam ownership
        await self._get_owned_exam(question.exam_id, current_user)

        return QuestionResponse.model_validate(question)

    # -----------------------------------------------------------------------
    # Update
    # -----------------------------------------------------------------------

    async def update_question(
        self,
        question_id: uuid.UUID,
        request: QuestionUpdate,
        current_user: User,
        *,
        request_id: str = "",
    ) -> QuestionResponse:
        """
        Update a question's content, marks, order, or options.

        The question_type cannot be changed (would invalidate existing answers).
        """
        from sqlalchemy import select
        from app.models.question import Question

        stmt = select(Question).where(Question.id == question_id)
        result = await self._db.execute(stmt)
        question = result.scalar_one_or_none()

        if question is None:
            raise NotFoundError(f"Question {question_id} not found.")

        # Verify exam ownership and DRAFT status
        exam = await self._get_owned_exam(question.exam_id, current_user)
        if exam.status not in (ExamStatus.DRAFT, ExamStatus.DRAFT.value):
            raise ValidationError(
                f"Cannot update questions on a {exam.status} exam. "
                "The exam must be in DRAFT status."
            )

        if request.content is not None:
            question.content = request.content
        if request.marks is not None:
            question.marks = request.marks
        if request.order_number is not None:
            question.order_number = request.order_number
        if request.options is not None:
            # Validate MCQ options if this is an MCQ question
            if question.question_type == QuestionType.MCQ:
                from app.schemas.question import MCQOptions
                MCQOptions(**request.options)
            question.options = request.options

        await self._db.commit()
        await self._db.refresh(question)

        log_security_event(
            SecurityEvent.QUESTION_UPDATED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/questions/{question_id}",
        )

        return QuestionResponse.model_validate(question)

    # -----------------------------------------------------------------------
    # Delete
    # -----------------------------------------------------------------------

    async def delete_question(
        self,
        question_id: uuid.UUID,
        current_user: User,
        *,
        request_id: str = "",
    ) -> None:
        """
        Delete a question.

        Restricted to DRAFT exams (cannot remove questions from published exams).
        """
        from sqlalchemy import select
        from app.models.question import Question

        stmt = select(Question).where(Question.id == question_id)
        result = await self._db.execute(stmt)
        question = result.scalar_one_or_none()

        if question is None:
            raise NotFoundError(f"Question {question_id} not found.")

        # Verify exam ownership and DRAFT status
        exam = await self._get_owned_exam(question.exam_id, current_user)
        if exam.status != ExamStatus.DRAFT:
            raise ValidationError(
                f"Cannot delete questions from a {exam.status} exam. "
                "The exam must be in DRAFT status."
            )

        await self._questions.delete(self._db, question)
        await self._db.commit()

        log_security_event(
            SecurityEvent.QUESTION_DELETED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/questions/{question_id}",
        )

    # -----------------------------------------------------------------------
    # Candidate assignment
    # -----------------------------------------------------------------------

    async def assign_candidates(
        self,
        exam_id: uuid.UUID,
        candidate_ids: list[uuid.UUID],
        current_user: User,
        *,
        request_id: str = "",
    ) -> tuple[int, int]:
        """
        Assign candidates to an exam.

        Returns (assigned_count, skipped_count).
        Duplicate assignments are rejected with 409 Conflict.
        """
        from app.repositories.candidate_repository import CandidateRepository
        from app.repositories.user_repository import UserRepository
        from app.core.constants import RoleName as Role

        # Verify exam ownership
        await self._get_owned_exam(exam_id, current_user)

        duplicate_ids = []
        for cid in set(candidate_ids):
            if await CandidateRepository.is_assigned(self._db, exam_id, cid):
                duplicate_ids.append(cid)
        if duplicate_ids:
            raise ConflictError("One or more candidates are already assigned to this exam.")

        # Filter to only valid CANDIDATE users
        user_repo = UserRepository(self._db)
        valid_candidate_ids = []
        for cid in candidate_ids:
            user = await user_repo.get_by_id(cid)
            if user and user.role and user.role.name == Role.CANDIDATE and user.is_active:
                valid_candidate_ids.append(cid)

        if not valid_candidate_ids:
            return 0, len(candidate_ids)

        assigned, skipped = await CandidateRepository.assign_candidates(
            self._db,
            exam_id=exam_id,
            candidate_ids=valid_candidate_ids,
            assigned_by=current_user.id,
        )
        # Count truly invalid (not-CANDIDATE) users as skipped too
        invalid_count = len(candidate_ids) - len(valid_candidate_ids)
        await self._db.commit()

        log_security_event(
            SecurityEvent.CANDIDATE_ASSIGNED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/exams/{exam_id}/candidates",
        )

        return assigned, skipped + invalid_count

    async def list_candidates(
        self,
        exam_id: uuid.UUID,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[dict], int]:
        """List candidates assigned to an exam (interviewer/admin only)."""
        from app.repositories.candidate_repository import CandidateRepository

        await self._get_owned_exam(exam_id, current_user)
        return await CandidateRepository.list_candidates(
            self._db, exam_id, skip=skip, limit=limit
        )

    async def remove_candidate(
        self,
        exam_id: uuid.UUID,
        candidate_id: uuid.UUID,
        current_user: User,
        *,
        request_id: str = "",
    ) -> None:
        """Remove a candidate from an exam."""
        from app.repositories.candidate_repository import CandidateRepository

        await self._get_owned_exam(exam_id, current_user)
        removed = await CandidateRepository.remove_candidate(
            self._db, exam_id, candidate_id
        )
        if not removed:
            raise NotFoundError(
                f"Candidate {candidate_id} is not assigned to exam {exam_id}."
            )
        await self._db.commit()

        log_security_event(
            SecurityEvent.CANDIDATE_REMOVED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/exams/{exam_id}/candidates/{candidate_id}",
        )

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    async def _get_owned_exam(self, exam_id: uuid.UUID, user: User):
        """
        Fetch an exam with ownership check.
        ADMIN can access any exam; INTERVIEWER only their own.
        Raises NotFoundError (vague) to prevent IDOR enumeration.
        """
        user_role = user.role.name if user.role else ""
        owner_id = None if user_role == RoleName.ADMIN else user.id

        exam = await self._exams.get_by_id_with_owner_check(
            self._db, exam_id, owner_id=owner_id
        )
        if exam is None:
            raise NotFoundError(f"Exam {exam_id} not found.")
        return exam

    async def _verify_candidate_assigned(
        self, exam_id: uuid.UUID, candidate_id: uuid.UUID
    ) -> None:
        """Verify a candidate is assigned to an exam."""
        from app.repositories.candidate_repository import CandidateRepository

        is_assigned = await CandidateRepository.is_assigned(
            self._db, exam_id, candidate_id
        )
        if not is_assigned:
            raise NotFoundError(f"Exam {exam_id} not found.")
