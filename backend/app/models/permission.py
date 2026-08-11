"""
app/models/permission.py
========================
SQLAlchemy 2.0 ORM model for the `permissions` table.

Permissions represent resource:action pairs (e.g. "exam:create").
They are seeded by Alembic and referenced via role_permissions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.role_permission import RolePermission


class Permission(UUIDMixin, TimestampMixin, Base):
    """
    A permission record representing a named capability.

    Permissions are linked to roles via the `role_permissions` join table.
    """

    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("name", name="uq_permissions_name"),
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Relationships ---
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Permission id={self.id} name={self.name!r}>"
