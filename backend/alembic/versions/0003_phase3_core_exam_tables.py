"""
Alembic Migration: 0003 - Phase 3 Core Exam Tables
==================================================
Creates the core exam portal tables required by the current SQLAlchemy models:
  - exams
  - questions
  - exam_candidates
  - exam_attempts
  - submissions
  - exam_results

Revision: 0003_phase3_core_exam_tables
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_phase3_core_exam_tables"
down_revision: str | None = "0002_session_replaced_by"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "exams",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'DRAFT'"),
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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
    op.create_index("ix_exams_id", "exams", ["id"])
    op.create_index("ix_exams_created_by", "exams", ["created_by"])
    op.create_index("ix_exams_status", "exams", ["status"])
    op.create_index("ix_exams_scheduled_at", "exams", ["scheduled_at"])

    op.create_table(
        "questions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "exam_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question_type", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("marks", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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
        sa.CheckConstraint("marks > 0", name="ck_questions_marks_positive"),
        sa.CheckConstraint("order_number >= 1", name="ck_questions_order_positive"),
    )
    op.create_index("ix_questions_id", "questions", ["id"])
    op.create_index("ix_questions_exam_id", "questions", ["exam_id"])
    op.create_index(
        "ix_questions_exam_id_order", "questions", ["exam_id", "order_number"]
    )

    op.create_table(
        "exam_candidates",
        sa.Column(
            "exam_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "assigned_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "exam_id",
            "candidate_id",
            name="uq_exam_candidates_exam_candidate",
        ),
    )
    op.create_index("ix_exam_candidates_exam_id", "exam_candidates", ["exam_id"])
    op.create_index(
        "ix_exam_candidates_candidate_id", "exam_candidates", ["candidate_id"]
    )

    op.create_table(
        "exam_attempts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "exam_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'IN_PROGRESS'"),
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.UniqueConstraint(
            "exam_id", "candidate_id", name="uq_exam_attempts_exam_candidate"
        ),
    )
    op.create_index("ix_exam_attempts_id", "exam_attempts", ["id"])
    op.create_index("ix_exam_attempts_exam_id", "exam_attempts", ["exam_id"])
    op.create_index(
        "ix_exam_attempts_candidate_id", "exam_attempts", ["candidate_id"]
    )
    op.create_index("ix_exam_attempts_status", "exam_attempts", ["status"])

    op.create_table(
        "submissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "attempt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exam_attempts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "answer_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("score_awarded", sa.Numeric(precision=6, scale=2), nullable=True),
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
        sa.UniqueConstraint(
            "attempt_id", "question_id", name="uq_submissions_attempt_question"
        ),
    )
    op.create_index("ix_submissions_id", "submissions", ["id"])
    op.create_index("ix_submissions_attempt_id", "submissions", ["attempt_id"])
    op.create_index("ix_submissions_question_id", "submissions", ["question_id"])

    op.create_table(
        "exam_results",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "attempt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exam_attempts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "exam_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("attempted_count", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("incorrect_count", sa.Integer(), nullable=False),
        sa.Column("total_marks", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("score", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("percentage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'EVALUATED'"),
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
        sa.UniqueConstraint("attempt_id", name="uq_exam_results_attempt_id"),
    )
    op.create_index("ix_exam_results_id", "exam_results", ["id"])
    op.create_index("ix_exam_results_attempt_id", "exam_results", ["attempt_id"])
    op.create_index("ix_exam_results_candidate_id", "exam_results", ["candidate_id"])
    op.create_index("ix_exam_results_exam_id", "exam_results", ["exam_id"])


def downgrade() -> None:
    op.drop_table("exam_results")
    op.drop_table("submissions")
    op.drop_table("exam_attempts")
    op.drop_table("exam_candidates")
    op.drop_table("questions")
    op.drop_table("exams")
