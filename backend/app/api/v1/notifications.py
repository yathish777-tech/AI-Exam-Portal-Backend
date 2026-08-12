from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import PAGINATION_DEFAULT_PAGE, PAGINATION_DEFAULT_PAGE_SIZE, PAGINATION_MAX_PAGE_SIZE, RoleName
from app.database.dependencies import get_db
from app.dependencies.roles import require_role
from app.models.user import User
from app.schemas.notification import NotificationListResponse, NotificationResponse, UnreadCountResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = Query(default=False),
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=1),
    page_size: int = Query(default=PAGINATION_DEFAULT_PAGE_SIZE, ge=1, le=PAGINATION_MAX_PAGE_SIZE),
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER, RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> NotificationListResponse:
    return await NotificationService(db).list_for_user(
        current_user.id, unread_only=unread_only, page=page, page_size=page_size
    )


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER, RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    return await NotificationService(db).mark_read(notification_id, current_user.id)


@router.patch("/read-all")
async def mark_all_read(
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER, RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    count = await NotificationService(db).mark_all_read(current_user.id)
    return {"updated_count": count}


@router.get("/unread-count", response_model=UnreadCountResponse)
async def unread_count(
    current_user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER, RoleName.CANDIDATE)),
    db: AsyncSession = Depends(get_db),
) -> UnreadCountResponse:
    return await NotificationService(db).get_unread_count(current_user.id)
