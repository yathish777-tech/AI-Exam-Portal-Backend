from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import PAGINATION_DEFAULT_PAGE, PAGINATION_DEFAULT_PAGE_SIZE, PAGINATION_MAX_PAGE_SIZE, RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.admin import AdminRoleChangeRequest, AdminUserListResponse, AdminUserResponse, AdminUserUpdate, SystemSettingUpdate
from app.schemas.analytics import PlatformStats
from app.schemas.proctoring_warning import WarningListResponse
from app.services.admin_service import AdminService
from app.services.analytics_service import AnalyticsService
from app.services.proctoring_service import ProctoringService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=PlatformStats)
async def get_admin_dashboard(
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> PlatformStats:
    return await AnalyticsService(db).get_platform_stats()


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    role: RoleName | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> AdminUserListResponse:
    return await AdminService(db).list_users(
        role=role, is_active=is_active, page=page, page_size=page_size
    )


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> AdminUserResponse:
    return await AdminService(db).get_user(user_id)


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: uuid.UUID,
    body: AdminUserUpdate,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> AdminUserResponse:
    return await AdminService(db).set_active(
        user_id,
        is_active=body.is_active,
        admin_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )


@router.patch("/users/{user_id}/role", response_model=AdminUserResponse)
async def change_user_role(
    user_id: uuid.UUID,
    body: AdminRoleChangeRequest,
    request: Request,
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> AdminUserResponse:
    return await AdminService(db).change_user_role(
        user_id,
        body.role,
        admin_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )


@router.get("/students", response_model=AdminUserListResponse)
async def list_students(
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> AdminUserListResponse:
    return await AdminService(db).list_users(
        role=RoleName.CANDIDATE, page=page, page_size=page_size
    )


@router.get("/students/{student_id}", response_model=AdminUserResponse)
async def get_student(
    student_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> AdminUserResponse:
    return await AdminService(db).get_user(student_id)


@router.get("/interviewers", response_model=AdminUserListResponse)
async def list_interviewers(
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> AdminUserListResponse:
    return await AdminService(db).list_users(
        role=RoleName.INTERVIEWER, page=page, page_size=page_size
    )


@router.get("/interviewers/{interviewer_id}", response_model=AdminUserResponse)
async def get_interviewer(
    interviewer_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> AdminUserResponse:
    return await AdminService(db).get_user(interviewer_id)


@router.get("/analytics", response_model=PlatformStats)
async def get_admin_analytics(
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> PlatformStats:
    return await AnalyticsService(db).get_platform_stats()


@router.get("/warnings", response_model=WarningListResponse)
async def list_warning_logs(
    attempt_id: uuid.UUID | None = Query(default=None),
    candidate_id: uuid.UUID | None = Query(default=None),
    violation_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=50, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> WarningListResponse:
    return await ProctoringService(db).list_all(
        attempt_id=attempt_id,
        candidate_id=candidate_id,
        violation_type=violation_type,
        severity=severity,
        page=page,
        page_size=page_size,
    )


@router.get("/activity-logs")
async def list_activity_logs(
    actor_id: uuid.UUID | None = Query(default=None),
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=50, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).list_activity_logs(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        page=page,
        page_size=page_size,
    )


@router.get("/settings")
async def list_settings(
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).list_settings()


@router.patch("/settings")
async def update_setting(
    body: SystemSettingUpdate,
    key: str = Query(..., min_length=1),
    current_user: User = Depends(require_role(RoleName.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).update_setting(key, body.value, admin_id=current_user.id)
