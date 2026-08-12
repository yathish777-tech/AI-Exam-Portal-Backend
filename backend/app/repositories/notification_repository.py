"""
app/repositories/notification_repository.py
=============================================
Database operations for the `notifications` table.

SECURITY NOTES:
- All queries are scoped to a specific user_id — prevents IDOR.
- Never query notifications without user_id filter in candidate/interviewer paths.
- Only ADMIN endpoints may query across all users.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    """Data-access layer for Notification records."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

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
        """Insert a new notification for a specific user."""
        notif = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            reference_id=reference_id,
            reference_type=reference_type,
            is_read=False,
        )
        self._db.add(notif)
        await self._db.flush()
        await self._db.refresh(notif)
        return notif

    async def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        """Return a notification by primary key."""
        result = await self._db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Notification]:
        """Return paginated notifications for a user, newest first."""
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)  # noqa: E712
        stmt = stmt.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def count_for_user(
        self, user_id: uuid.UUID, *, unread_only: bool = False
    ) -> int:
        """Count notifications for a user."""
        stmt = select(func.count()).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)  # noqa: E712
        result = await self._db.execute(stmt)
        return result.scalar_one()

    async def mark_read(
        self, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """
        Mark a single notification as read.
        Scoped to user_id to prevent IDOR.
        Returns True if a row was updated.
        """
        result = await self._db.execute(
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .values(is_read=True)
            .returning(Notification.id)
        )
        await self._db.flush()
        return result.scalar_one_or_none() is not None

    async def mark_all_read(self, user_id: uuid.UUID) -> int:
        """
        Mark all unread notifications for a user as read.
        Returns the count of updated rows.
        """
        result = await self._db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
            .values(is_read=True)
            .returning(Notification.id)
        )
        await self._db.flush()
        return len(result.scalars().all())
