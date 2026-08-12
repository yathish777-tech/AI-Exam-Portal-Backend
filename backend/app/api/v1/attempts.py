"""
app/api/v1/attempts.py
========================
API endpoints for exam attempts, auto-save, and submission.

Authorization:
- POST /exams/{exam_id}/start:         CANDIDATE only
- GET /attempts/{attempt_id}:           CANDIDATE (own) | ADMIN | INTERVIEWER (own exam)
- POST /attempts/{attempt_id}/answers:  CANDIDATE only
- POST /attempts/{attempt_id}/submit:   CANDIDATE only

SECURITY:
- `candidate_id` is NEVER accepted from the request — always from JWT.
- ONE ATTEMPT PER CANDIDATE PER EXAM — enforced at service + DB level.
- Auto-save is idempotent (PostgreSQL upsert).
- Submission is transactional.
- After submission, answers cannot be changed.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.exam_attempt import AttemptResponse, AttemptStartResponse
from app.schemas.submission import AnswerSaveRequest, AnswerSaveResponse, SubmitRequest
from app.services.attempt_service import AttemptService
from app.services.submission_service import SubmissionService

router = APIRouter(tags=["Attempts"])


# ---------------------------------------------------------------------------
# Start exam attempt
# ---------------------------------------------------------------------------

@router.post(
    "/exams/{exam_id}/start",
    response_model=AttemptStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start an exam attempt",
    description=(
        "Starts an exam attempt for the authenticated candidate. "
        "Only one attempt per candidate per exam is allowed. "
        "If an in-progress attempt exists, it is resumed."
    ),
)
async def start_attempt(
    exam_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> AttemptStartResponse:
    service = AttemptService(db)
    return await service.start_attempt(
        exam_id,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )


# ---------------------------------------------------------------------------
# Get attempt details
# ---------------------------------------------------------------------------

@router.get(
    "/attempts/{attempt_id}",
    response_model=AttemptResponse,
    summary="Get attempt details",
    description=(
        "Returns attempt details. "
        "Candidates can only see their own attempt. "
        "Interviewers see attempts for their exam. "
        "Admins see any attempt."
    ),
)
async def get_attempt(
    attempt_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(
        require_role(RoleName.CANDIDATE, RoleName.ADMIN, RoleName.INTERVIEWER)
    ),
    db: AsyncSession = Depends(get_db),
) -> AttemptResponse:
    service = AttemptService(db)
    return await service.get_attempt(attempt_id, current_user)


# ---------------------------------------------------------------------------
# Auto-save answer
# ---------------------------------------------------------------------------

@router.post(
    "/attempts/{attempt_id}/answers",
    response_model=AnswerSaveResponse,
    status_code=status.HTTP_200_OK,
    summary="Auto-save an answer",
    description=(
        "Upserts a single answer for a question in an active attempt. "
        "Can be called repeatedly — each call replaces the previous answer. "
        "The attempt must be IN_PROGRESS."
    ),
)
async def save_answer(
    attempt_id: uuid.UUID,
    body: AnswerSaveRequest,
    request: Request,
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> AnswerSaveResponse:
    service = SubmissionService(db)
    return await service.save_answer(
        attempt_id,
        body,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )


# ---------------------------------------------------------------------------
# Submit exam
# ---------------------------------------------------------------------------

@router.post(
    "/attempts/{attempt_id}/submit",
    status_code=status.HTTP_200_OK,
    summary="Submit exam",
    description=(
        "Finalizes and submits an exam attempt. "
        "Evaluates all MCQ answers server-side. "
        "Non-MCQ answers are marked PENDING_EVALUATION. "
        "The attempt cannot be modified after submission."
    ),
)
async def submit_exam(
    attempt_id: uuid.UUID,
    body: SubmitRequest,
    request: Request,
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = SubmissionService(db)
    return await service.submit_exam(
        attempt_id,
        body.answers,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )
