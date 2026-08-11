"""
app/database/base.py
====================
SQLAlchemy 2.0 declarative base with shared mixins.

All ORM models must inherit from `Base`.
`TimestampMixin` automatically manages created_at / updated_at in UTC.
`UUIDMixin` provides a UUID4 primary key.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """Return the current time in UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """
    Project-wide SQLAlchemy declarative base.

    All models must extend this class so that Alembic autogenerate
    can discover them via `Base.metadata`.
    """

    pass


class UUIDMixin:
    """
    Provides a UUID4 primary key column named `id`.

    The UUID is generated at the Python layer (not the DB layer)
    so it is available before the INSERT flush.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampMixin:
    """
    Provides `created_at` and `updated_at` columns (UTC, timezone-aware).

    - `created_at` is set once on INSERT via `server_default=func.now()`.
    - `updated_at` is updated on every UPDATE via `onupdate=func.now()`.

    Both columns use PostgreSQL's `TIMESTAMPTZ` (timestamp with time zone)
    to ensure consistent UTC storage regardless of server locale.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
