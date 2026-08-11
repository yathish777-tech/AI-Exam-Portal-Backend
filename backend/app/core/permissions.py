"""
app/core/permissions.py
=======================
Role-Based Access Control (RBAC) permission definitions.

Design:
- Permissions are resource + action pairs (e.g. "exam:read").
- Each role has a fixed set of permissions defined here.
- Authorization decisions MUST be made using the role loaded from the
  database, NOT from the JWT claims.
- This module is the single source of truth for RBAC rules.

Extension:
- Add new permissions to the `Permission` enum.
- Update `ROLE_PERMISSIONS` accordingly.
- If you need fine-grained permissions stored in the DB, add a migration
  to populate the `permissions` and `role_permissions` tables and update
  this module to load from DB.
"""

from __future__ import annotations

from enum import StrEnum

from app.core.constants import RoleName


class Permission(StrEnum):
    """
    All available permissions in the system.

    Format: "resource:action"
    """

    # --- User management ---
    USER_READ_ANY = "user:read_any"
    USER_UPDATE_ANY = "user:update_any"
    USER_ACTIVATE = "user:activate"
    USER_DEACTIVATE = "user:deactivate"
    USER_ASSIGN_ROLE = "user:assign_role"

    # --- Exam management ---
    EXAM_CREATE = "exam:create"
    EXAM_READ_ANY = "exam:read_any"
    EXAM_UPDATE = "exam:update"
    EXAM_DELETE = "exam:delete"
    EXAM_PUBLISH = "exam:publish"

    # --- Questions ---
    QUESTION_CREATE = "question:create"
    QUESTION_UPDATE = "question:update"
    QUESTION_DELETE = "question:delete"
    QUESTION_READ_ANY = "question:read_any"

    # --- Candidate / Exam attempt ---
    EXAM_ATTEMPT = "exam:attempt"
    EXAM_SUBMIT = "exam:submit"
    EXAM_READ_OWN = "exam:read_own"
    RESULT_READ_OWN = "result:read_own"

    # --- Results / Reports ---
    RESULT_READ_ANY = "result:read_any"
    REPORT_VIEW = "report:view"

    # --- Proctoring ---
    PROCTORING_MONITOR = "proctoring:monitor"
    PROCTORING_VIEW_WARNINGS = "proctoring:view_warnings"

    # --- System ---
    SYSTEM_SETTINGS = "system:settings"
    AUDIT_LOG_READ = "audit_log:read"


# ---------------------------------------------------------------------------
# Role → Permission mapping
# ---------------------------------------------------------------------------
# This is the authoritative RBAC table for backend enforcement.
# Frontend route guards are purely UX — backend MUST enforce independently.
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    RoleName.ADMIN: {
        # Admins have all permissions
        Permission.USER_READ_ANY,
        Permission.USER_UPDATE_ANY,
        Permission.USER_ACTIVATE,
        Permission.USER_DEACTIVATE,
        Permission.USER_ASSIGN_ROLE,
        Permission.EXAM_CREATE,
        Permission.EXAM_READ_ANY,
        Permission.EXAM_UPDATE,
        Permission.EXAM_DELETE,
        Permission.EXAM_PUBLISH,
        Permission.QUESTION_CREATE,
        Permission.QUESTION_UPDATE,
        Permission.QUESTION_DELETE,
        Permission.QUESTION_READ_ANY,
        Permission.RESULT_READ_ANY,
        Permission.REPORT_VIEW,
        Permission.PROCTORING_MONITOR,
        Permission.PROCTORING_VIEW_WARNINGS,
        Permission.SYSTEM_SETTINGS,
        Permission.AUDIT_LOG_READ,
    },
    RoleName.INTERVIEWER: {
        Permission.EXAM_CREATE,
        Permission.EXAM_READ_ANY,
        Permission.EXAM_UPDATE,
        Permission.EXAM_PUBLISH,
        Permission.QUESTION_CREATE,
        Permission.QUESTION_UPDATE,
        Permission.QUESTION_READ_ANY,
        Permission.RESULT_READ_ANY,
        Permission.REPORT_VIEW,
        Permission.PROCTORING_MONITOR,
        Permission.PROCTORING_VIEW_WARNINGS,
        Permission.USER_READ_ANY,
    },
    RoleName.CANDIDATE: {
        Permission.EXAM_ATTEMPT,
        Permission.EXAM_SUBMIT,
        Permission.EXAM_READ_OWN,
        Permission.RESULT_READ_OWN,
    },
}


def has_permission(role_name: str, permission: Permission) -> bool:
    """
    Check if a role has a specific permission.

    Args:
        role_name: The role name string (e.g. "ADMIN").
        permission: The Permission enum value to check.

    Returns:
        True if the role has the permission.
    """
    return permission in ROLE_PERMISSIONS.get(role_name, set())


def get_role_permissions(role_name: str) -> set[Permission]:
    """Return all permissions for a given role name."""
    return ROLE_PERMISSIONS.get(role_name, set())
