"""
app/models/system_setting.py
==============================
SQLAlchemy 2.0 ORM model for the `system_settings` table.

SECURITY NOTES:
- Only ADMIN users can read or modify system settings (enforced at router).
- `key` is unique — no duplicate setting keys permitted.
- Values are stored as text; the service layer handles type coercion.
- Sensitive values (e.g., secrets) must NOT be stored here — use env vars.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class SystemSetting(UUIDMixin, TimestampMixin, Base):
    """
    A single application-level configuration key-value pair.

    Settings are managed by ADMIN users through the admin API.
    They are NOT environment variables — use for runtime-configurable
    values only (e.g., max_attempts_per_exam, allow_registration).

    NEVER store secrets, API keys, or passwords in this table.
    """

    __tablename__ = "system_settings"
    __table_args__ = (
        UniqueConstraint("key", name="uq_system_settings_key"),
        Index("ix_system_settings_key", "key"),
    )

    # Dot-namespaced key: e.g. "exam.max_duration_minutes"
    key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # String-serialized value. Service layer handles bool/int coercion.
    value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Description of what this setting controls.
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Expected value type hint for the UI: "string" | "integer" | "boolean"
    value_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="string",
        server_default="string",
    )

    # Who last modified this setting.
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # --- Relationships ---
    editor: Mapped["User | None"] = relationship("User", foreign_keys=[updated_by])

    def __repr__(self) -> str:
        return f"<SystemSetting key={self.key!r} value={self.value!r}>"
