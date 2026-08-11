"""
Alembic Migration: 0001 — Authentication Tables
================================================
Creates all tables required for the authentication module:
  - roles
  - permissions
  - role_permissions
  - users
  - sessions
  - password_reset_otps

Also:
  - Enables the PostgreSQL `citext` extension (case-insensitive email).
  - Seeds the three default roles: ADMIN, INTERVIEWER, CANDIDATE.

REVERSIBLE: downgrade() drops all tables in reverse dependency order.

PRE-REQUISITES:
  - PostgreSQL user must have SUPERUSER or CREATEROLE privilege to
    create the citext extension (or the extension must already exist).
  - If the extension already exists in your DB, the
    `CREATE EXTENSION IF NOT EXISTS citext` is a no-op.
  - gen_random_uuid() is built-in from PostgreSQL 13+. No extension needed.

Revision: 0001_auth_tables
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision: str = "0001_auth_tables"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # Enable CITEXT extension (idempotent)
    # -----------------------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    # -----------------------------------------------------------------------
    # roles
    # -----------------------------------------------------------------------
    op.create_table(
        "roles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"])
    op.create_index("ix_roles_id", "roles", ["id"])

    # -----------------------------------------------------------------------
    # permissions
    # -----------------------------------------------------------------------
    op.create_table(
        "permissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("name", name="uq_permissions_name"),
    )
    op.create_index("ix_permissions_name", "permissions", ["name"])
    op.create_index("ix_permissions_id", "permissions", ["id"])

    # -----------------------------------------------------------------------
    # role_permissions (join table)
    # -----------------------------------------------------------------------
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "permission_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.UniqueConstraint(
            "role_id", "permission_id", name="uq_role_permissions"
        ),
    )

    # -----------------------------------------------------------------------
    # users
    # -----------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        # CITEXT provides case-insensitive uniqueness for email
        sa.Column("email", postgresql.CITEXT, nullable=False, unique=True),
        sa.Column("password_hash", sa.String(72), nullable=False),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            default=True,
            server_default="true",
        ),
        sa.Column(
            "last_login_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role_id", "users", ["role_id"])

    # -----------------------------------------------------------------------
    # sessions
    # -----------------------------------------------------------------------
    op.create_table(
        "sessions",
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
        sa.Column(
            "token_family_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("jwt_jti", sa.String(36), nullable=False, unique=True),
        sa.Column("current_refresh_token_hash", sa.String(64), nullable=False),
        sa.Column("ip_address", postgresql.INET, nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_sessions_id", "sessions", ["id"])
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_index("ix_sessions_token_family_id", "sessions", ["token_family_id"])
    op.create_index("ix_sessions_jwt_jti", "sessions", ["jwt_jti"])
    op.create_index(
        "ix_sessions_current_refresh_token_hash",
        "sessions",
        ["current_refresh_token_hash"],
    )

    # -----------------------------------------------------------------------
    # password_reset_otps
    # -----------------------------------------------------------------------
    op.create_table(
        "password_reset_otps",
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
        sa.Column("otp_hash", sa.String(64), nullable=False),
        sa.Column(
            "purpose",
            sa.String(50),
            nullable=False,
            server_default="password_reset",
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "attempt_count",
            sa.SmallInteger,
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "is_used",
            sa.Boolean,
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_otp_id", "password_reset_otps", ["id"])
    op.create_index("ix_otp_user_id", "password_reset_otps", ["user_id"])

    # -----------------------------------------------------------------------
    # Seed default roles
    # -----------------------------------------------------------------------
    op.execute(
        sa.text(
            """
            INSERT INTO roles (id, name, description, created_at, updated_at)
            VALUES
                (:admin_id, 'ADMIN', 'System administrator with full access', NOW(), NOW()),
                (:interviewer_id, 'INTERVIEWER', 'Exam creator and evaluator', NOW(), NOW()),
                (:candidate_id, 'CANDIDATE', 'Exam participant', NOW(), NOW())
            ON CONFLICT (name) DO NOTHING
            """
        ).bindparams(
            admin_id=uuid.uuid4(),
            interviewer_id=uuid.uuid4(),
            candidate_id=uuid.uuid4(),
        )
    )


def downgrade() -> None:
    """Drop all authentication tables in reverse dependency order."""
    op.drop_index("ix_otp_user_id", table_name="password_reset_otps")
    op.drop_index("ix_otp_id", table_name="password_reset_otps")
    op.drop_table("password_reset_otps")

    op.drop_index("ix_sessions_current_refresh_token_hash", table_name="sessions")
    op.drop_index("ix_sessions_jwt_jti", table_name="sessions")
    op.drop_index("ix_sessions_token_family_id", table_name="sessions")
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_index("ix_sessions_id", table_name="sessions")
    op.drop_table("sessions")

    op.drop_index("ix_users_role_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")

    op.drop_table("role_permissions")

    op.drop_index("ix_permissions_name", table_name="permissions")
    op.drop_index("ix_permissions_id", table_name="permissions")
    op.drop_table("permissions")

    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_index("ix_roles_id", table_name="roles")
    op.drop_table("roles")

    # Note: We do NOT drop the citext extension in downgrade because
    # other tables/schemas in the same DB might use it.
    # op.execute("DROP EXTENSION IF EXISTS citext")
