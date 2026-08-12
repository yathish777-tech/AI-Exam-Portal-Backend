"""
app/services/exam_service.py
==============================
Business logic for exam management.

ARCHITECTURE:
- All DB access goes through repositories.
- All business rules (status transitions, ownership, authorization) are here.
- No HTTP concerns (Request/Response) and no direct SQL.

SECURITY:
- `created_by` is ALWAYS set from authenticated user — never from request.
- Status transitions are enforced here (DRAFT → PUBLISHED → SCHEDULED → COMPLETED).
- Interviewers can only manage their own exams; Admins can manage any exam.
- Deleting a PUBLISHED exam is forbidden (use CANCELLED status).
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ExamStatus, RoleName, SecurityEvent
from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError, ValidationError
from app.core.logging import log_security_event
from app.models.user import User
from app.repositories.exam_repository import ExamRepository
from app.schemas.exam import (
    ExamCreate,
    ExamListItem,
    ExamResponse,
    ExamScheduleRequest,
    ExamUpdate,
)


class ExamService:
    """
    Orchestrates exam lifecycle operations.

    All methods are async and accept an AsyncSession from the dependency.
    The session is committed by the calling router after the service returns.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._exams = ExamRepository

    # -----------------------------------------------------------------------
    # Create
    # -----------------------------------------------------------------------

    async def create_exam(
        self,
        request: ExamCreate,
        current_user: User,
        *,
        request_id: str = "",
    ) -> ExamResponse:
        """
        Create a new exam in DRAFT status.

        SECURITY:
        - `created_by` is set from `current_user.id` — never from request.
        - Only ADMIN and INTERVIEWER can create exams (enforced at router).
        """
        from app.models.exam import Exam

        exam = Exam(
            created_by=current_user.id,
            title=request.title,
            description=request.description,
            duration_minutes=request.duration_minutes,
            scheduled_at=request.scheduled_at,
            config=request.config,
            status=ExamStatus.DRAFT,
        )

        db_exam = await self._exams.save(self._db, exam)
        await self._db.commit()
        await self._db.refresh(db_exam)

        log_security_event(
            SecurityEvent.EXAM_CREATED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint="/exams",
        )

        question_count = await self._exams.get_question_count(self._db, db_exam.id)
        return ExamResponse.from_orm_with_count(db_exam, question_count)

    # -----------------------------------------------------------------------
    # Read
    # -----------------------------------------------------------------------

    async def get_exam(
        self,
        exam_id: uuid.UUID,
        current_user: User,
    ) -> ExamResponse:
        """
        Return exam details.

        - ADMIN: can view any exam.
        - INTERVIEWER: can only view their own exams.
        - CANDIDATE: access denied (use candidate-specific endpoints).
        """
        owner_id = self._get_owner_filter(current_user)
        exam = await self._exams.get_by_id_with_owner_check(
            self._db, exam_id, owner_id=owner_id
        )
        if exam is None:
            raise NotFoundError(f"Exam {exam_id} not found.")

        question_count = await self._exams.get_question_count(self._db, exam_id)
        return ExamResponse.from_orm_with_count(exam, question_count)

    async def list_exams(
        self,
        current_user: User,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[ExamListItem], int]:
        """
        Return a paginated list of exams, scoped by user role.

        - ADMIN: sees all exams.
        - INTERVIEWER: sees only their own exams.
        """
        owner_id = self._get_owner_filter(current_user)
        exams, total = await self._exams.list_exams(
            self._db,
            owner_id=owner_id,
            status=status,
            skip=skip,
            limit=limit,
        )

        items = []
        for exam in exams:
            q_count = await self._exams.get_question_count(self._db, exam.id)
            items.append(
                ExamListItem(
                    id=exam.id,
                    title=exam.title,
                    status=exam.status,
                    duration_minutes=exam.duration_minutes,
                    scheduled_at=exam.scheduled_at,
                    created_at=exam.created_at,
                    question_count=q_count,
                )
            )
        return items, total

    # -----------------------------------------------------------------------
    # Update
    # -----------------------------------------------------------------------

    async def update_exam(
        self,
        exam_id: uuid.UUID,
        request: ExamUpdate,
        current_user: User,
        *,
        request_id: str = "",
    ) -> ExamResponse:
        """
        Update exam fields.

        SECURITY:
        - Only DRAFT exams can be freely updated.
        - PUBLISHED/SCHEDULED exams can only update description and config.
        - Status is NOT updatable via this method — use lifecycle endpoints.
        """
        exam = await self._get_owned_exam(exam_id, current_user)

        # Restrict which fields can be changed on non-DRAFT exams
        if exam.status not in (ExamStatus.DRAFT, ExamStatus.DRAFT.value):
            # On published exams only description and config can change
            if request.title is not None or request.duration_minutes is not None:
                raise ValidationError(
                    "Cannot change title or duration of a published exam. "
                    "Cancel and recreate the exam if structural changes are needed."
                )

        if request.title is not None:
            exam.title = request.title
        if request.description is not None:
            exam.description = request.description
        if request.duration_minutes is not None:
            exam.duration_minutes = request.duration_minutes
        if request.scheduled_at is not None:
            exam.scheduled_at = request.scheduled_at
        if request.config is not None:
            exam.config = request.config

        await self._db.commit()
        await self._db.refresh(exam)

        log_security_event(
            SecurityEvent.EXAM_UPDATED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/exams/{exam_id}",
        )

        question_count = await self._exams.get_question_count(self._db, exam_id)
        return ExamResponse.from_orm_with_count(exam, question_count)

    # -----------------------------------------------------------------------
    # Delete
    # -----------------------------------------------------------------------

    async def delete_exam(
        self,
        exam_id: uuid.UUID,
        current_user: User,
        *,
        request_id: str = "",
    ) -> None:
        """
        Delete an exam. Only DRAFT exams can be deleted.

        PUBLISHED/SCHEDULED exams must be CANCELLED first, not deleted,
        to preserve the audit record.
        """
        exam = await self._get_owned_exam(exam_id, current_user)

        if exam.status not in (ExamStatus.DRAFT, ExamStatus.DRAFT.value):
            raise ValidationError(
                f"Cannot delete an exam with status '{exam.status}'. "
                "Only DRAFT exams can be deleted. Use the cancel endpoint to cancel a published exam."
            )

        await self._exams.delete(self._db, exam)
        await self._db.commit()

        log_security_event(
            SecurityEvent.EXAM_DELETED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/exams/{exam_id}",
        )

    # -----------------------------------------------------------------------
    # Lifecycle transitions
    # -----------------------------------------------------------------------

    async def publish_exam(
        self,
        exam_id: uuid.UUID,
        current_user: User,
        *,
        request_id: str = "",
    ) -> ExamResponse:
        """
        Transition exam from DRAFT → PUBLISHED.

        Requires at least one question. Cannot publish an already-published exam.
        """
        exam = await self._get_owned_exam(exam_id, current_user)

        if exam.status != ExamStatus.DRAFT:
            raise ValidationError(
                f"Cannot publish exam with status '{exam.status}'. "
                "Only DRAFT exams can be published."
            )

        question_count = await self._exams.get_question_count(self._db, exam_id)
        if question_count == 0:
            raise ValidationError(
                "Cannot publish an exam with no questions. "
                "Add at least one question before publishing."
            )

        exam.status = ExamStatus.PUBLISHED
        await self._db.commit()
        await self._db.refresh(exam)

        log_security_event(
            SecurityEvent.EXAM_PUBLISHED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/exams/{exam_id}/publish",
        )

        return ExamResponse.from_orm_with_count(exam, question_count)

    async def schedule_exam(
        self,
        exam_id: uuid.UUID,
        request: ExamScheduleRequest,
        current_user: User,
        *,
        request_id: str = "",
    ) -> ExamResponse:
        """
        Transition exam from PUBLISHED → SCHEDULED with a specific start time.
        """
        exam = await self._get_owned_exam(exam_id, current_user)

        if exam.status not in (ExamStatus.PUBLISHED, ExamStatus.PUBLISHED.value):
            raise ValidationError(
                f"Cannot schedule exam with status '{exam.status}'. "
                "Only PUBLISHED exams can be scheduled."
            )

        exam.status = ExamStatus.SCHEDULED
        exam.scheduled_at = request.scheduled_at
        await self._db.commit()
        await self._db.refresh(exam)

        log_security_event(
            SecurityEvent.EXAM_SCHEDULED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/exams/{exam_id}/schedule",
        )

        question_count = await self._exams.get_question_count(self._db, exam_id)
        return ExamResponse.from_orm_with_count(exam, question_count)

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _get_owner_filter(self, user: User) -> uuid.UUID | None:
        """
        Return owner_id filter for repository queries.
        ADMIN sees all; INTERVIEWER sees only their own.
        """
        user_role = user.role.name if user.role else ""
        if user_role == RoleName.ADMIN:
            return None  # No filter — admin sees all
        return user.id  # Interviewer sees only their exams

    async def _get_owned_exam(self, exam_id: uuid.UUID, user: User):
        """
        Fetch an exam, applying ownership filter for non-admins.
        Raises NotFoundError (deliberately vague) to prevent IDOR enumeration.
        """
        owner_id = self._get_owner_filter(user)
        exam = await self._exams.get_by_id_with_owner_check(
            self._db, exam_id, owner_id=owner_id
        )
        if exam is None:
            raise NotFoundError(f"Exam {exam_id} not found.")
        return exam
