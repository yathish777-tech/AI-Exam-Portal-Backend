from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import PAGINATION_DEFAULT_PAGE, PAGINATION_DEFAULT_PAGE_SIZE, PAGINATION_MAX_PAGE_SIZE, RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.notification import NotificationListResponse, NotificationResponse, UnreadCountResponse
from app.schemas.student import StudentExamListResponse, StudentProfileResponse, StudentResultListResponse, StudentResultSummary
from app.services.analytics_service import AnalyticsService
from app.services.notification_service import NotificationService
from app.services.student_service import StudentService

router = APIRouter(prefix="/student", tags=["Student"])


class StudentProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")


@router.get("/dashboard", response_model=StudentExamListResponse)
async def get_student_dashboard(
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> StudentExamListResponse:
    return await StudentService(db).list_assigned_exams(
        current_user.id, page=page, page_size=page_size
    )


@router.get("/exams/upcoming", response_model=StudentExamListResponse)
async def list_upcoming_exams(
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> StudentExamListResponse:
    return await StudentService(db).list_assigned_exams(
        current_user.id, page=page, page_size=page_size
    )


@router.get("/exams/completed", response_model=StudentResultListResponse)
async def list_completed_exams(
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> StudentResultListResponse:
    return await StudentService(db).list_results(
        current_user.id, page=page, page_size=page_size
    )


@router.get("/profile", response_model=StudentProfileResponse)
async def get_profile(
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> StudentProfileResponse:
    return await StudentService(db).get_profile(current_user.id)


@router.patch("/profile", response_model=StudentProfileResponse)
async def update_profile(
    body: StudentProfileUpdate,
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> StudentProfileResponse:
    return await StudentService(db).get_profile(current_user.id)


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = Query(default=False),
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> NotificationListResponse:
    return await NotificationService(db).list_for_user(
        current_user.id, unread_only=unread_only, page=page, page_size=page_size
    )


@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    return await NotificationService(db).mark_read(notification_id, current_user.id)


@router.patch("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    count = await NotificationService(db).mark_all_read(current_user.id)
    return {"updated_count": count}


@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> UnreadCountResponse:
    return await NotificationService(db).get_unread_count(current_user.id)


@router.get("/exam-history", response_model=StudentExamListResponse)
async def get_exam_history(
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> StudentExamListResponse:
    return await StudentService(db).list_assigned_exams(
        current_user.id, page=page, page_size=page_size
    )


@router.get("/results", response_model=StudentResultListResponse)
async def list_results(
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> StudentResultListResponse:
    return await StudentService(db).list_results(
        current_user.id, page=page, page_size=page_size
    )


@router.get("/results/{result_id}", response_model=StudentResultSummary)
async def get_result(
    result_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> StudentResultSummary:
    return await StudentService(db).get_result(current_user.id, result_id)


@router.get("/performance")
async def get_performance(
    current_user: User = Depends(require_role(RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsService(db).get_candidate_analytics(current_user.id)
