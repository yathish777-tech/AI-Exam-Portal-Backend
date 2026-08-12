"""
app/repositories/log_repository.py
=====================================
Database operations for the `activity_logs` table.

SECURITY NOTES:
- Logs are append-only. No UPDATE or DELETE methods are provided.
- ADMIN-only read access enforced at the router/service layer.
- Log entries must never contain passwords, tokens, or raw secrets.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog


class LogRepository:
    """Data-access layer for ActivityLog records (append-only)."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        *,
        actor_id: uuid.UUID | None,
        action: str,
        resource_type: str | None = None,
        resource_id: uuid.UUID | None = None,
        description: str | None = None,
        extra: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> ActivityLog:
        """
        Append a new activity log entry.

        Must not raise — log failures should be caught and swallowed
        at the service layer to avoid breaking primary request flow.
        """
        log = ActivityLog(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            extra=extra,
            ip_address=ip_address,
        )
        self._db.add(log)
        await self._db.flush()
        return log

    async def list_all(
        self,
        *,
        actor_id: uuid.UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ActivityLog]:
        """
        Return paginated activity logs with optional filters.
        ADMIN only — enforced at the router layer.
        """
        stmt = select(ActivityLog)
        if actor_id is not None:
            stmt = stmt.where(ActivityLog.actor_id == actor_id)
        if action is not None:
            stmt = stmt.where(ActivityLog.action == action)
        if resource_type is not None:
            stmt = stmt.where(ActivityLog.resource_type == resource_type)
        stmt = stmt.order_by(ActivityLog.created_at.desc()).limit(limit).offset(offset)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def count_all(
        self,
        *,
        actor_id: uuid.UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> int:
        """Count activity logs matching the given filters."""
        stmt = select(func.count())
        if actor_id is not None:
            stmt = stmt.where(ActivityLog.actor_id == actor_id)
        if action is not None:
            stmt = stmt.where(ActivityLog.action == action)
        if resource_type is not None:
            stmt = stmt.where(ActivityLog.resource_type == resource_type)
        result = await self._db.execute(stmt)
        return result.scalar_one()
