"""
app/services/notification_service.py
=======================================
Business logic for notifications.

SECURITY NOTES:
- All list/count operations are scoped to the requesting user's id.
- Notifications are created server-side only — never from client-supplied data.
- mark_read validates user_id ownership before updating.
"""

from __future__ import annotations

import uuid
from math import ceil

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)


class NotificationService:
    """Notification delivery and management."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = NotificationRepository(db)

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: str,
        reference_id: uuid.UUID | None = None,
        reference_type: str | None = None,
    ) -> Notification:
        """Create a new notification for a user (server-side only)."""
        notif = await self._repo.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            reference_id=reference_id,
            reference_type=reference_type,
        )
        await self._db.commit()
        return notif

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
    ) -> NotificationListResponse:
        """Return paginated notifications for the authenticated user."""
        offset = (page - 1) * page_size
        items = await self._repo.list_for_user(
            user_id, unread_only=unread_only, limit=page_size, offset=offset
        )
        total = await self._repo.count_for_user(user_id, unread_only=unread_only)
        unread_count = await self._repo.count_for_user(user_id, unread_only=True)
        total_pages = ceil(total / page_size) if page_size > 0 else 0

        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in items],
            total=total,
            unread_count=unread_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_unread_count(self, user_id: uuid.UUID) -> UnreadCountResponse:
        """Return the number of unread notifications for the user."""
        count = await self._repo.count_for_user(user_id, unread_only=True)
        return UnreadCountResponse(unread_count=count)

    async def mark_read(
        self,
        notification_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> NotificationResponse:
        """
        Mark a notification as read.
        Validates that the notification belongs to the requesting user (IDOR guard).
        """
        updated = await self._repo.mark_read(
            notification_id, requesting_user_id
        )
        if not updated:
            # Either doesn't exist or belongs to another user — treat as 404.
            raise NotFoundError("Notification not found.")

        notif = await self._repo.get_by_id(notification_id)
        await self._db.commit()
        return NotificationResponse.model_validate(notif)

    async def mark_all_read(self, user_id: uuid.UUID) -> int:
        """Mark all unread notifications for a user as read. Returns count."""
        count = await self._repo.mark_all_read(user_id)
        await self._db.commit()
        return count

    # ------------------------------------------------------------------
    # Helper: send typed notifications from other services
    # ------------------------------------------------------------------

    async def notify_exam_assigned(
        self,
        user_id: uuid.UUID,
        exam_id: uuid.UUID,
        exam_title: str,
    ) -> None:
        """Send an exam-assigned notification (called from exam service)."""
        await self.create(
            user_id=user_id,
            notification_type="EXAM_ASSIGNED",
            title="New Exam Assigned",
            message=f"You have been assigned to the exam: {exam_title}",
            reference_id=exam_id,
            reference_type="exam",
        )

    async def notify_result_published(
        self,
        user_id: uuid.UUID,
        exam_id: uuid.UUID,
        exam_title: str,
    ) -> None:
        """Send a result-published notification."""
        await self.create(
            user_id=user_id,
            notification_type="RESULT_PUBLISHED",
            title="Exam Result Available",
            message=f"Your result for '{exam_title}' is now available.",
            reference_id=exam_id,
            reference_type="exam",
        )
