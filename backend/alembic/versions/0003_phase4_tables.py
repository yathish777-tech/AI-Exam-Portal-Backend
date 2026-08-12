"""
Alembic Migration: 0003 — Phase 4 Tables
==========================================
Creates tables for Phase 4 features:
  - notifications
  - proctoring_warnings
  - activity_logs
  - system_settings

REVERSIBLE: downgrade() drops all tables in reverse dependency order.

Revision: 0003_phase4_tables
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision: str = "0004_phase4_tables"
down_revision: str | None = "0003_phase3_core_exam_tables"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # notifications
    # -----------------------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column(
            "reference_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column(
            "is_read",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index(
        "ix_notifications_user_id_is_read",
        "notifications",
        ["user_id", "is_read"],
    )

    # -----------------------------------------------------------------------
    # proctoring_warnings
    # -----------------------------------------------------------------------
    op.create_table(
        "proctoring_warnings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "attempt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exam_attempts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("violation_type", sa.String(50), nullable=False),
        sa.Column(
            "severity",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'LOW'"),
        ),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_proctoring_warnings_attempt_id", "proctoring_warnings", ["attempt_id"]
    )
    op.create_index(
        "ix_proctoring_warnings_candidate_id", "proctoring_warnings", ["candidate_id"]
    )
    op.create_index(
        "ix_proctoring_warnings_violation_type",
        "proctoring_warnings",
        ["violation_type"],
    )

    # -----------------------------------------------------------------------
    # activity_logs
    # -----------------------------------------------------------------------
    op.create_table(
        "activity_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "actor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column(
            "resource_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("extra", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_activity_logs_actor_id", "activity_logs", ["actor_id"])
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"])
    op.create_index(
        "ix_activity_logs_resource_type", "activity_logs", ["resource_type"]
    )
    op.create_index("ix_activity_logs_created_at", "activity_logs", ["created_at"])

    # -----------------------------------------------------------------------
    # system_settings
    # -----------------------------------------------------------------------
    op.create_table(
        "system_settings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("key", sa.String(255), nullable=False, unique=True),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "value_type",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'string'"),
        ),
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_unique_constraint("uq_system_settings_key", "system_settings", ["key"])
    op.create_index("ix_system_settings_key", "system_settings", ["key"])


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("system_settings")
    op.drop_table("activity_logs")
    op.drop_table("proctoring_warnings")
    op.drop_table("notifications")
