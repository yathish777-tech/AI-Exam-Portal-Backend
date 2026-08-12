from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import PAGINATION_DEFAULT_PAGE, PAGINATION_MAX_PAGE_SIZE, RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.proctoring_warning import WarningCreate, WarningListResponse, WarningResponse, WarningSummary
from app.services.proctoring_service import ProctoringService

router = APIRouter(prefix="/proctoring", tags=["Proctoring"])


@router.post("/attempts/{attempt_id}/warnings", response_model=WarningResponse)
async def create_warning(
    attempt_id: uuid.UUID,
    body: WarningCreate,
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> WarningResponse:
    return await ProctoringService(db).log_warning(attempt_id, current_user.id, body)


@router.get("/attempts/{attempt_id}/warnings", response_model=WarningListResponse)
async def list_attempt_warnings(
    attempt_id: uuid.UUID,
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=50, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER, RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> WarningListResponse:
    role = current_user.role.name if current_user.role else ""
    return await ProctoringService(db).list_by_attempt(
        attempt_id,
        requesting_user_id=current_user.id,
        is_admin_or_interviewer=role in {RoleName.ADMIN, RoleName.INTERVIEWER},
        page=page,
        page_size=page_size,
    )


@router.get("/attempts/{attempt_id}/warnings/summary", response_model=WarningSummary)
async def get_attempt_warning_summary(
    attempt_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> WarningSummary:
    return await ProctoringService(db).get_attempt_summary(attempt_id)
