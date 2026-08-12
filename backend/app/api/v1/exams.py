"""
app/api/v1/exams.py
====================
API endpoints for exam management and candidate assignment.

Authorization:
- POST/PATCH/DELETE/publish/schedule: ADMIN or INTERVIEWER (owner)
- GET (list/detail): ADMIN or INTERVIEWER (scoped)
- Candidate assignment: ADMIN or INTERVIEWER (owner)
- GET candidates: ADMIN or INTERVIEWER (owner)
- DELETE candidate: ADMIN or INTERVIEWER (owner)

SECURITY:
- `created_by` is NEVER accepted from request body — always from JWT.
- Status transitions go through dedicated endpoints (no direct status patch).
- Candidates cannot access this router (enforced by require_role guards).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import PAGINATION_DEFAULT_PAGE_SIZE, PAGINATION_MAX_PAGE_SIZE, RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.exam import (
    ExamCreate,
    ExamListItem,
    ExamResponse,
    ExamScheduleRequest,
    ExamUpdate,
)
from app.schemas.exam_candidate import (
    CandidateAssignRequest as CandidateAssign,
    CandidateAssignmentResponse,
    CandidateItem,
    CandidateListResponse,
)
from app.services.exam_service import ExamService

router = APIRouter(prefix="/exams", tags=["Exams"])


# ---------------------------------------------------------------------------
# Create exam
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=ExamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new exam",
    description="Creates an exam in DRAFT status. Only ADMIN and INTERVIEWER can create exams.",
)
async def create_exam(
    body: ExamCreate,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> ExamResponse:
    service = ExamService(db)
    return await service.create_exam(
        body,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )


# ---------------------------------------------------------------------------
# List exams
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=dict,
    summary="List exams",
    description="Returns a paginated list of exams. ADMIN sees all; INTERVIEWER sees their own.",
)
async def list_exams(
    request: Request,
    status_filter: str | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(
        default=PAGINATION_DEFAULT_PAGE_SIZE,
        ge=1,
        le=PAGINATION_MAX_PAGE_SIZE,
        description="Page size",
    ),
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = ExamService(db)
    items, total = await service.list_exams(
        current_user,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return {
        "success": True,
        "data": {
            "items": [item.model_dump() for item in items],
            "total": total,
            "skip": skip,
            "limit": limit,
        },
    }


# ---------------------------------------------------------------------------
# Get exam by ID
# ---------------------------------------------------------------------------

@router.get(
    "/{exam_id}",
    response_model=ExamResponse,
    summary="Get exam details",
    description="Returns full exam details. ADMIN can see any exam; INTERVIEWER only their own.",
)
async def get_exam(
    exam_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> ExamResponse:
    service = ExamService(db)
    return await service.get_exam(exam_id, current_user)


# ---------------------------------------------------------------------------
# Update exam
# ---------------------------------------------------------------------------

@router.patch(
    "/{exam_id}",
    response_model=ExamResponse,
    summary="Update exam fields",
    description="Partial update of exam metadata. Status not updatable here — use /publish or /schedule.",
)
async def update_exam(
    exam_id: uuid.UUID,
    body: ExamUpdate,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> ExamResponse:
    service = ExamService(db)
    return await service.update_exam(
        exam_id,
        body,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )


# ---------------------------------------------------------------------------
# Delete exam
# ---------------------------------------------------------------------------

@router.delete(
    "/{exam_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete exam",
    description="Deletes a DRAFT exam permanently. Published exams cannot be deleted.",
)
async def delete_exam(
    exam_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = ExamService(db)
    await service.delete_exam(
        exam_id,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )


# ---------------------------------------------------------------------------
# Publish exam
# ---------------------------------------------------------------------------

@router.post(
    "/{exam_id}/publish",
    response_model=ExamResponse,
    summary="Publish exam",
    description="Transitions exam from DRAFT → PUBLISHED. Requires at least one question.",
)
async def publish_exam(
    exam_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> ExamResponse:
    service = ExamService(db)
    return await service.publish_exam(
        exam_id,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )


# ---------------------------------------------------------------------------
# Schedule exam
# ---------------------------------------------------------------------------

@router.post(
    "/{exam_id}/schedule",
    response_model=ExamResponse,
    summary="Schedule exam",
    description="Transitions exam from PUBLISHED → SCHEDULED with a specific start time.",
)
async def schedule_exam(
    exam_id: uuid.UUID,
    body: ExamScheduleRequest,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> ExamResponse:
    service = ExamService(db)
    return await service.schedule_exam(
        exam_id,
        body,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )


# ---------------------------------------------------------------------------
# Candidate assignment
# ---------------------------------------------------------------------------

@router.post(
    "/{exam_id}/candidates",
    response_model=CandidateAssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign candidates to exam",
    description=(
        "Assigns one or more candidate users to an exam. "
        "Duplicate assignments are silently skipped."
    ),
)
async def assign_candidates(
    exam_id: uuid.UUID,
    body: CandidateAssign,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> CandidateAssignmentResponse:
    from app.services.question_service import QuestionService
    service = QuestionService(db)
    assigned, skipped = await service.assign_candidates(
        exam_id,
        body.candidate_ids,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )
    return CandidateAssignmentResponse(
        assigned_count=assigned,
        skipped_count=skipped,
        message=f"Assigned {assigned} candidate(s). Skipped {skipped} (already assigned or invalid).",
    )


@router.get(
    "/{exam_id}/candidates",
    response_model=CandidateListResponse,
    summary="List candidates assigned to exam",
)
async def list_candidates(
    exam_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> CandidateListResponse:
    from app.services.question_service import QuestionService
    service = QuestionService(db)
    items, total = await service.list_candidates(
        exam_id, current_user, skip=skip, limit=limit
    )
    candidate_items = [
        CandidateItem(
            candidate_id=item["candidate_id"],
            email=item["email"],
            assigned_at=item["assigned_at"],
            assigned_by=item["assigned_by"],
        )
        for item in items
    ]
    return CandidateListResponse(items=candidate_items, total=total)


@router.delete(
    "/{exam_id}/candidates/{candidate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove candidate from exam",
)
async def remove_candidate(
    exam_id: uuid.UUID,
    candidate_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> None:
    from app.services.question_service import QuestionService
    service = QuestionService(db)
    await service.remove_candidate(
        exam_id,
        candidate_id,
        current_user,
        request_id=getattr(request.state, "request_id", ""),
    )


# ---------------------------------------------------------------------------
# Exam results (interviewer/admin view)
# ---------------------------------------------------------------------------

@router.get(
    "/{exam_id}/results",
    summary="List results for an exam",
    description="Returns paginated results for all candidates in an exam. Interviewer/Admin only.",
)
async def list_exam_results(
    exam_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.services.result_service import ResultService
    service = ResultService(db)
    result = await service.list_exam_results(
        exam_id, current_user, skip=skip, limit=limit
    )
    return {"success": True, "data": result.model_dump()}
