"""
app/repositories/base.py
=========================
Generic async repository base class.

All future domain repositories (ExamRepository, QuestionRepository, etc.)
should inherit from BaseRepository[T] to gain consistent CRUD primitives
and a shared contract for the service layer.

Design decisions:
- Typed with Generic[T] so subclasses get full type-checker support.
- All methods accept an AsyncSession — no session is stored on the instance,
  keeping the repository stateless and safe for dependency injection.
- Queries use SQLAlchemy 2.x select() style exclusively.
- Raw string SQL is never used in this base class.
- Database errors (IntegrityError, etc.) are NOT caught here; subclasses
  should catch and convert them to appropriate AppException subclasses.
"""

from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

# T must be a SQLAlchemy ORM model class that inherits from Base.
T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Generic repository providing basic async CRUD operations.

    Usage in a subclass::

        class ExamRepository(BaseRepository[Exam]):
            model = Exam

            async def get_by_title(self, db: AsyncSession, title: str) -> Exam | None:
                result = await db.execute(
                    select(Exam).where(Exam.title == title)
                )
                return result.scalar_one_or_none()

    The ``model`` class attribute MUST be defined in every subclass.
    """

    model: type[T]

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @classmethod
    async def get_by_id(
        cls,
        db: AsyncSession,
        record_id: uuid.UUID,
    ) -> T | None:
        """
        Return a single record by primary key (UUID), or None if not found.

        Args:
            db: The current async database session.
            record_id: The UUID primary key of the record.

        Returns:
            The ORM model instance, or None.
        """
        result = await db.execute(
            select(cls.model).where(cls.model.id == record_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, db: AsyncSession) -> list[T]:
        """
        Return all records of this model type (no pagination).

        WARNING: Only use on small reference tables (e.g. roles, permissions).
        For large tables, always use paginated queries in the subclass.

        Args:
            db: The current async database session.

        Returns:
            A list of ORM model instances (may be empty).
        """
        result = await db.execute(select(cls.model))
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    @classmethod
    async def save(cls, db: AsyncSession, instance: T) -> T:
        """
        Persist a new or modified ORM instance and flush to the DB.

        Does NOT commit — callers are responsible for committing the
        transaction at the appropriate service-layer boundary.

        Args:
            db: The current async database session.
            instance: The ORM model instance to persist.

        Returns:
            The refreshed ORM model instance (with DB-generated fields).
        """
        db.add(instance)
        await db.flush()
        await db.refresh(instance)
        return instance

    @classmethod
    async def delete(cls, db: AsyncSession, instance: T) -> None:
        """
        Delete an ORM instance and flush the deletion.

        Does NOT commit — callers are responsible for committing.

        Args:
            db: The current async database session.
            instance: The ORM model instance to delete.
        """
        await db.delete(instance)
        await db.flush()
