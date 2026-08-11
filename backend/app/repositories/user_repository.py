"""
app/repositories/user_repository.py
=====================================
Database operations for the `users` table.

SECURITY NOTES:
- All queries use SQLAlchemy ORM (parameterized) — never string concatenation.
- Email is normalized to lowercase before all queries, complementing the
  CITEXT column's case-insensitive comparison.
- `update_password` and `update_last_login` are atomic operations.
- IntegrityError (duplicate email) is caught and re-raised as ConflictError
  so callers never see raw PostgreSQL errors.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.models.user import User


class UserRepository:
    """Data-access layer for User records."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return a User by primary key, or None if not found."""
        result = await self._db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Return a User by email (case-insensitive via CITEXT), or None.

        Email is lowercased before querying as a defence-in-depth measure
        even though CITEXT handles case-insensitivity at the DB layer.
        """
        normalized = email.strip().lower()
        result = await self._db.execute(
            select(User).where(User.email == normalized)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
        role_id: uuid.UUID,
    ) -> User:
        """
        Insert a new User record.

        Raises:
            ConflictError: If the email already exists (IntegrityError).
        """
        user = User(
            email=email.strip().lower(),
            password_hash=password_hash,
            role_id=role_id,
            is_active=True,
        )
        self._db.add(user)
        try:
            await self._db.flush()  # detect constraint violations early
            await self._db.refresh(user)
        except IntegrityError:
            await self._db.rollback()
            raise ConflictError(
                message="An account with this email already exists.",
                error_code="EMAIL_ALREADY_EXISTS",
            )
        return user

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """Update `last_login_at` to the current UTC timestamp."""
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.now(timezone.utc))
        )
        await self._db.flush()

    async def update_password(
        self,
        user_id: uuid.UUID,
        new_password_hash: str,
    ) -> None:
        """
        Update a user's password hash.

        SECURITY: Only the bcrypt hash is accepted — this function
        must never be called with a plaintext password.
        """
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_hash=new_password_hash)
        )
        await self._db.flush()

    async def set_active(self, user_id: uuid.UUID, *, is_active: bool) -> None:
        """Enable or disable a user account."""
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=is_active)
        )
        await self._db.flush()
