"""
app/models/__init__.py
======================
Re-exports all ORM models so that Alembic's `autogenerate` discovers
the full table metadata when it inspects `Base.metadata`.

Every new model MUST be imported here.

Import order: independent models first, then dependent ones.
This prevents circular import issues during metadata inspection.
"""

from app.database.base import Base  # noqa: F401 — needed for Base.metadata

# --- Independent models (no FK dependencies on each other) ---
from app.models.role import Role  # noqa: F401
from app.models.permission import Permission  # noqa: F401

# --- Join tables ---
from app.models.role_permission import RolePermission  # noqa: F401

# --- User (depends on Role) ---
from app.models.user import User  # noqa: F401

# --- Session and OTP (depend on User) ---
from app.models.session import UserSession  # noqa: F401
from app.models.otp import PasswordResetOTP  # noqa: F401

# --- Phase 3: Exam portal models ---
# Import in dependency order: Exam first, then its children.
from app.models.exam import Exam  # noqa: F401
from app.models.question import Question  # noqa: F401
from app.models.exam_candidate import ExamCandidate  # noqa: F401
from app.models.exam_attempt import ExamAttempt  # noqa: F401
from app.models.submission import Submission  # noqa: F401
from app.models.exam_result import ExamResult  # noqa: F401

__all__ = [
    "Base",
    # Auth
    "Role",
    "Permission",
    "RolePermission",
    "User",
    "UserSession",
    "PasswordResetOTP",
    # Exam portal
    "Exam",
    "Question",
    "ExamCandidate",
    "ExamAttempt",
    "Submission",
    "ExamResult",
]
