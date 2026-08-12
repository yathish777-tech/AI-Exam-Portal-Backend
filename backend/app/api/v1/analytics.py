from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.analytics import CandidateAnalytics, ExamAnalytics, PlatformStats
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/platform", response_model=PlatformStats)
async def platform_stats(
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> PlatformStats:
    return await AnalyticsService(db).get_platform_stats()


@router.get("/exams/{exam_id}", response_model=ExamAnalytics)
async def exam_analytics(
    exam_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> ExamAnalytics:
    role = current_user.role.name if current_user.role else ""
    return await AnalyticsService(db).get_exam_analytics(
        exam_id,
        requesting_user_id=current_user.id,
        is_admin=role == RoleName.ADMIN,
    )


@router.get("/candidates/{candidate_id}", response_model=CandidateAnalytics)
async def candidate_analytics(
    candidate_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> CandidateAnalytics:
    return await AnalyticsService(db).get_candidate_analytics(candidate_id)
