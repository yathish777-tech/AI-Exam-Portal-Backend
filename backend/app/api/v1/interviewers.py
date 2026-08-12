from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import PAGINATION_DEFAULT_PAGE, PAGINATION_DEFAULT_PAGE_SIZE, PAGINATION_MAX_PAGE_SIZE, RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.interviewer import InterviewerCandidateListResponse, InterviewerExamListResponse
from app.schemas.proctoring_warning import WarningListResponse
from app.schemas.report import ExamReport
from app.services.interviewer_service import InterviewerService
from app.services.proctoring_service import ProctoringService
from app.services.report_service import ReportService

router = APIRouter(prefix="/interviewer", tags=["Interviewer"])


@router.get("/dashboard", response_model=InterviewerExamListResponse)
async def get_dashboard(
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> InterviewerExamListResponse:
    return await InterviewerService(db).list_my_exams(
        current_user.id, page=page, page_size=page_size
    )


@router.get("/exams/{exam_id}/candidates", response_model=InterviewerCandidateListResponse)
async def list_interviewer_candidates(
    exam_id: uuid.UUID,
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> InterviewerCandidateListResponse:
    return await InterviewerService(db).list_my_candidates(
        current_user.id, exam_id=exam_id, page=page, page_size=page_size
    )


@router.get("/exams/{exam_id}/warnings", response_model=WarningListResponse)
async def list_exam_warnings(
    exam_id: uuid.UUID,
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=50, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> WarningListResponse:
    await InterviewerService(db).verify_exam_owner(exam_id, current_user.id)
    return await ProctoringService(db).list_all(page=page, page_size=page_size)


@router.get("/attempts/{attempt_id}/activity")
async def list_attempt_activity(
    attempt_id: uuid.UUID,
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=50, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
):
    return await InterviewerService(db).list_attempt_activity(
        attempt_id, current_user.id, page=page, page_size=page_size
    )


@router.post("/exams/{exam_id}/results/publish")
async def publish_results(
    exam_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
):
    return await InterviewerService(db).publish_results(exam_id, current_user.id)


@router.get("/exams/{exam_id}/reports", response_model=ExamReport)
async def get_exam_report(
    exam_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.INTERVIEWER)),
    db: AsyncSession = Depends(get_db),
) -> ExamReport:
    return await ReportService(db).generate_exam_report(
        exam_id, requesting_user_id=current_user.id, is_admin=False
    )
