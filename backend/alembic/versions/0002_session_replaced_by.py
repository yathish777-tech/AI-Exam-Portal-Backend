"""Add refresh-token rotation lineage to sessions.

Revision ID: 0002_session_replaced_by
Revises: 0001_auth_tables
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_session_replaced_by"
down_revision: str | None = "0001_auth_tables"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("replaced_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_sessions_replaced_by_sessions",
        "sessions",
        "sessions",
        ["replaced_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_sessions_replaced_by", "sessions", ["replaced_by"])


def downgrade() -> None:
    op.drop_index("ix_sessions_replaced_by", table_name="sessions")
    op.drop_constraint(
        "fk_sessions_replaced_by_sessions",
        "sessions",
        type_="foreignkey",
    )
    op.drop_column("sessions", "replaced_by")
