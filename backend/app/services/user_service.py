"""
app/services/user_service.py
==============================
Shared user operations used by admin, student, and interviewer services.

SECURITY NOTES:
- Never accepts role, id, or status from client request bodies.
- `get_by_id` validates user exists before returning to caller.
- Password hashing lives in auth_service; this service handles profile ops.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import func, select

from app.core.constants import RoleName
from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.models.role import Role
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository


class UserService:
    """Shared user management operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._user_repo = UserRepository(db)
        self._role_repo = RoleRepository(db)

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        """Return a user by ID or raise NotFoundError."""
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        return user

    async def list_users_by_role(
        self,
        role_name: RoleName,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        """
        Return paginated users filtered by role.
        Returns (items, total_count).
        """
        stmt_count = (
            select(func.count())
            .select_from(User)
            .join(Role, User.role_id == Role.id)
            .where(Role.name == role_name.value)
        )
        count_result = await self._db.execute(stmt_count)
        total = count_result.scalar_one()

        stmt = (
            select(User)
            .join(Role, User.role_id == Role.id)
            .where(Role.name == role_name.value)
            .order_by(User.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        result = await self._db.execute(stmt)
        users = list(result.scalars().all())
        return users, total

    async def list_all_users(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        """Return paginated users with optional active filter."""
        stmt_count = select(func.count()).select_from(User)
        stmt = select(User)
        if is_active is not None:
            stmt_count = stmt_count.where(User.is_active == is_active)
            stmt = stmt.where(User.is_active == is_active)

        count_result = await self._db.execute(stmt_count)
        total = count_result.scalar_one()

        stmt = stmt.order_by(User.created_at.desc()).limit(page_size).offset(
            (page - 1) * page_size
        )
        result = await self._db.execute(stmt)
        users = list(result.scalars().all())
        return users, total

    async def set_active(
        self, user_id: uuid.UUID, *, is_active: bool
    ) -> User:
        """Enable or disable a user account. Returns updated user."""
        user = await self.get_by_id(user_id)
        await self._user_repo.set_active(user_id, is_active=is_active)
        await self._db.commit()
        await self._db.refresh(user)
        return user

    async def change_role(
        self,
        user_id: uuid.UUID,
        new_role: RoleName,
    ) -> User:
        """Change a user's role. ADMIN only (enforced at router)."""
        user = await self.get_by_id(user_id)
        role = await self._role_repo.get_by_name(new_role.value)
        if role is None:
            raise NotFoundError(f"Role '{new_role}' not found in database.")
        user.role_id = role.id
        self._db.add(user)
        await self._db.flush()
        await self._db.commit()
        await self._db.refresh(user)
        return user
