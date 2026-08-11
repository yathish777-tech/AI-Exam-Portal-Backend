"""
app/dependencies/roles.py
=========================
FastAPI dependency factory for Role-Based Access Control (RBAC).

SECURITY:
- Role is always checked against the DATABASE-LOADED user object,
  not against JWT claims. JWT role claim is informational only.
- A user can NEVER change their own role via the roles API (there
  is no such endpoint in this module — role changes are admin-only
  operations handled in admin endpoints).
- AuthorizationError (403) messages are generic — they do not reveal
  which specific role was required.

Usage:
    from app.dependencies.roles import require_role
    from app.core.constants import RoleName

    @router.get("/admin/dashboard")
    async def admin_only(
        user: User = Depends(require_role(RoleName.ADMIN))
    ):
        ...

    # Multiple roles:
    @router.get("/staff/portal")
    async def staff_only(
        user: User = Depends(require_role(RoleName.ADMIN, RoleName.INTERVIEWER))
    ):
        ...
"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Request

from app.core.constants import RoleName, SecurityEvent
from app.core.exceptions import AuthorizationError
from app.core.logging import log_security_event
from app.dependencies.auth import get_current_user
from app.models.user import User


def require_role(*allowed_roles: RoleName) -> Callable:
    """
    Return a FastAPI dependency that enforces role membership.

    Args:
        *allowed_roles: One or more RoleName values that are permitted.

    Returns:
        A FastAPI dependency function that returns the authenticated User
        if the role check passes, or raises AuthorizationError (403).

    Example:
        @router.get("/admin")
        async def admin(user = Depends(require_role(RoleName.ADMIN))):
            ...
    """
    allowed_set = {role.value for role in allowed_roles}

    async def _check_role(
        request: Request,
        user: User = Depends(get_current_user),
    ) -> User:
        user_role = user.role.name if user.role else ""

        if user_role not in allowed_set:
            request_id = getattr(request.state, "request_id", "")
            log_security_event(
                SecurityEvent.AUTHORIZATION_FAILED,
                request_id=request_id,
                user_id=str(user.id),
                ip_address=request.client.host if request.client else "",
                endpoint=str(request.url.path),
                success=False,
                detail=f"Role '{user_role}' not in allowed roles",
            )
            raise AuthorizationError()

        return user

    return _check_role


def require_admin() -> Callable:
    """Shortcut: require ADMIN role."""
    return require_role(RoleName.ADMIN)


def require_interviewer() -> Callable:
    """Shortcut: require INTERVIEWER role (or ADMIN)."""
    return require_role(RoleName.ADMIN, RoleName.INTERVIEWER)


def require_candidate() -> Callable:
    """Shortcut: require CANDIDATE role."""
    return require_role(RoleName.CANDIDATE)
