"""
app/repositories/role_repository.py
=====================================
Database operations for the `roles` table.

Roles are read-only from the application perspective — they are
seeded by Alembic and managed by administrators, not by regular
API flows.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role


class RoleRepository:
    """Data-access layer for Role records."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_name(self, name: str) -> Role | None:
        """Return a Role by name (case-insensitive), or None."""
        result = await self._db.execute(
            select(Role).where(Role.name == name.upper())
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Role]:
        """Return all roles."""
        result = await self._db.execute(select(Role))
        return list(result.scalars().all())
