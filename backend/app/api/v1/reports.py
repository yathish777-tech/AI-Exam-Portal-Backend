from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.report import CandidateReport, ExamReport
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/exams/{exam_id}", response_model=ExamReport)
async def exam_report(
    exam_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> ExamReport:
    role = current_user.role.name if current_user.role else ""
    return await ReportService(db).generate_exam_report(
        exam_id,
        requesting_user_id=current_user.id,
        is_admin=role == RoleName.ADMIN,
    )


@router.get("/candidates/{candidate_id}", response_model=CandidateReport)
async def candidate_report(
    candidate_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> CandidateReport:
    return await ReportService(db).generate_candidate_report(candidate_id)
