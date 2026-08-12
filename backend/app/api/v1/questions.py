"""
app/api/v1/questions.py
========================
API endpoints for question management within exams.

Authorization:
- POST (create):  ADMIN or INTERVIEWER (exam owner)
- GET (list):     ADMIN, INTERVIEWER (owner), or CANDIDATE (assigned to exam)
- GET (detail):   ADMIN or INTERVIEWER (owner)
- PATCH (update): ADMIN or INTERVIEWER (owner)
- DELETE:         ADMIN or INTERVIEWER (owner)

SECURITY:
- Candidates receive QuestionCandidateResponse (correct_index stripped).
- `exam_id` is taken from the URL, not the body — verified server-side.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionCandidateResponse, QuestionResponse, QuestionUpdate
from app.services.question_service import QuestionService

router = APIRouter(tags=["Questions"])


# ---------------------------------------------------------------------------
# Create question in exam
# ---------------------------------------------------------------------------

@router.post(
    "/exams/{exam_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a question to an exam",
    description="Creates a question in the specified exam. Exam must be in DRAFT status.",
)
async def create_question(
    exam_id: uuid.UUID,
    body: QuestionCreate,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> QuestionResponse:
    service = QuestionService(db)
    return await service.create_question(
        exam_id,
        body,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )


# ---------------------------------------------------------------------------
# List questions in exam (role-aware response)
# ---------------------------------------------------------------------------

@router.get(
    "/exams/{exam_id}/questions",
    summary="List questions for an exam",
    description=(
        "Returns questions for an exam. "
        "Candidates receive sanitized responses (MCQ correct_index is stripped). "
        "Interviewers/Admins receive full question data including correct answers."
    ),
)
async def list_questions(
    exam_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(
        require_role(RoleName.ADMIN, RoleName.INTERVIEWER, RoleName.CANDIDATE)
    ),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = QuestionService(db)
    questions = await service.list_questions(exam_id, current_user)
    return {
        "success": True,
        "data": {
            "items": [q.model_dump() for q in questions],
            "total": len(questions),
        },
    }


# ---------------------------------------------------------------------------
# Get single question
# ---------------------------------------------------------------------------

@router.get(
    "/questions/{question_id}",
    response_model=QuestionResponse,
    summary="Get question details",
    description="Returns full question details including correct answer. Interviewer/Admin only.",
)
async def get_question(
    question_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> QuestionResponse:
    service = QuestionService(db)
    return await service.get_question(question_id, current_user)


# ---------------------------------------------------------------------------
# Update question
# ---------------------------------------------------------------------------

@router.patch(
    "/questions/{question_id}",
    response_model=QuestionResponse,
    summary="Update a question",
    description="Partial update of question content, marks, ordering, or options.",
)
async def update_question(
    question_id: uuid.UUID,
    body: QuestionUpdate,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> QuestionResponse:
    service = QuestionService(db)
    return await service.update_question(
        question_id,
        body,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )


# ---------------------------------------------------------------------------
# Delete question
# ---------------------------------------------------------------------------

@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a question",
    description="Deletes a question. The exam must be in DRAFT status.",
)
async def delete_question(
    question_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = QuestionService(db)
    await service.delete_question(
        question_id,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )
