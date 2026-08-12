"""
app/api/v1/results.py
======================
API endpoints for exam result retrieval.

Authorization:
- GET /attempts/{attempt_id}/result:   CANDIDATE (own) | ADMIN | INTERVIEWER (own exam)

SECURITY:
- Candidates can only access their own results (IDOR prevention in service).
- Interviewers can only access results for their own exams.
- Score, percentage, and is_correct are computed server-side — never client.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.result import ResultResponse
from app.services.result_service import ResultService

router = APIRouter(tags=["Results"])


# ---------------------------------------------------------------------------
# Get result for an attempt
# ---------------------------------------------------------------------------

@router.get(
    "/attempts/{attempt_id}/result",
    response_model=ResultResponse,
    summary="Get result for an attempt",
    description=(
        "Returns the evaluated result for a submitted attempt. "
        "Candidates can only see their own result. "
        "Includes optional per-question answer breakdown via ?include_answers=true."
    ),
)
async def get_attempt_result(
    attempt_id: uuid.UUID,
    request: Request,
    include_answers: bool = Query(
        default=False,
        description="Include per-question answer breakdown in the response.",
    ),
    current_user: User = Depends(
        require_role(RoleName.CANDIDATE, RoleName.ADMIN, RoleName.INTERVIEWER)
    ),
    db: AsyncSession = Depends(get_db),
) -> ResultResponse:
    service = ResultService(db)
    return await service.get_attempt_result(
        attempt_id,
        current_user,
        include_answers=include_answers,
    )
