"""
app/models/role.py
==================
SQLAlchemy 2.0 ORM model for the `roles` table.

ASSUMPTIONS (compatible with final ER diagram):
- Roles have a fixed set of names (ADMIN, INTERVIEWER, CANDIDATE).
- Roles are seeded via Alembic migration — not created by users.
- Role assignment to users is via users.role_id FK.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.role_permission import RolePermission


class Role(UUIDMixin, TimestampMixin, Base):
    """
    Represents an application role (e.g. ADMIN, INTERVIEWER, CANDIDATE).

    Roles are not created by end users. They are seeded at migration time.
    """

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("name", name="uq_roles_name"),
    )

    # Role name — must match RoleName enum values
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Relationships ---
    users: Mapped[list["User"]] = relationship("User", back_populates="role")
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name!r}>"
