"""
app/services/admin_service.py
================================
Business logic for Admin API endpoints.

SECURITY NOTES:
- Every method in this service is ADMIN only (enforced at the router layer).
- User IDs, roles, and statuses are never accepted from request bodies for
  privilege operations — they come from path parameters validated here.
- Mass assignment prevented: only explicitly listed fields are accepted.
- Activity logging is best-effort — failures are swallowed to not break flow.
"""

from __future__ import annotations

import uuid
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import RoleName
from app.core.exceptions import ConflictError, NotFoundError
from app.models.role import Role
from app.models.system_setting import SystemSetting
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.repositories.log_repository import LogRepository
from app.schemas.admin import (
    ActivityLogListResponse,
    ActivityLogResponse,
    AdminUserListResponse,
    AdminUserResponse,
    SystemSettingResponse,
)
from app.services.user_service import UserService


class AdminService:
    """Admin management operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._user_repo = UserRepository(db)
        self._role_repo = RoleRepository(db)
        self._log_repo = LogRepository(db)
        self._user_service = UserService(db)

    # ------------------------------------------------------------------
    # User Management
    # ------------------------------------------------------------------

    async def list_users(
        self,
        *,
        role: RoleName | None = None,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> AdminUserListResponse:
        """Return paginated users with optional role/active filters."""
        if role is not None:
            users, total = await self._user_service.list_users_by_role(
                role, page=page, page_size=page_size
            )
        else:
            users, total = await self._user_service.list_all_users(
                page=page, page_size=page_size, is_active=is_active
            )

        total_pages = ceil(total / page_size) if page_size > 0 else 0
        return AdminUserListResponse(
            items=[
                AdminUserResponse(
                    id=u.id,
                    email=u.email,
                    role=u.role.name if u.role else "UNKNOWN",
                    is_active=u.is_active,
                    created_at=u.created_at,
                    last_login_at=u.last_login_at,
                )
                for u in users
            ],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_user(self, user_id: uuid.UUID) -> AdminUserResponse:
        """Return a single user's details."""
        user = await self._user_service.get_by_id(user_id)
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            role=user.role.name if user.role else "UNKNOWN",
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )

    async def set_active(
        self,
        user_id: uuid.UUID,
        *,
        is_active: bool,
        admin_id: uuid.UUID,
        ip_address: str | None = None,
    ) -> AdminUserResponse:
        """Enable or disable a user account. Logs the action."""
        user = await self._user_service.set_active(user_id, is_active=is_active)
        action = "USER_ACTIVATED" if is_active else "USER_DEACTIVATED"
        try:
            await self._log_repo.create(
                actor_id=admin_id,
                action=action,
                resource_type="user",
                resource_id=user_id,
                description=f"User {user.email} {'activated' if is_active else 'deactivated'} by admin.",
                ip_address=ip_address,
            )
            await self._db.commit()
        except Exception:
            pass  # logging is best-effort

        return AdminUserResponse(
            id=user.id,
            email=user.email,
            role=user.role.name if user.role else "UNKNOWN",
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )

    async def change_user_role(
        self,
        user_id: uuid.UUID,
        new_role: RoleName,
        *,
        admin_id: uuid.UUID,
        ip_address: str | None = None,
    ) -> AdminUserResponse:
        """Change a user's role. Logs the action."""
        user = await self._user_service.change_role(user_id, new_role)
        try:
            await self._log_repo.create(
                actor_id=admin_id,
                action="USER_ROLE_CHANGED",
                resource_type="user",
                resource_id=user_id,
                description=f"Role changed to {new_role.value}.",
                ip_address=ip_address,
            )
            await self._db.commit()
        except Exception:
            pass

        return AdminUserResponse(
            id=user.id,
            email=user.email,
            role=user.role.name if user.role else "UNKNOWN",
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )

    # ------------------------------------------------------------------
    # Activity Logs
    # ------------------------------------------------------------------

    async def list_activity_logs(
        self,
        *,
        actor_id: uuid.UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> ActivityLogListResponse:
        """Return paginated activity logs with optional filters."""
        offset = (page - 1) * page_size
        items = await self._log_repo.list_all(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            limit=page_size,
            offset=offset,
        )
        total = await self._log_repo.count_all(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
        )
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        return ActivityLogListResponse(
            items=[ActivityLogResponse.model_validate(l) for l in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    # ------------------------------------------------------------------
    # System Settings
    # ------------------------------------------------------------------

    async def list_settings(self) -> list[SystemSettingResponse]:
        """Return all system settings."""
        result = await self._db.execute(
            select(SystemSetting).order_by(SystemSetting.key)
        )
        settings = result.scalars().all()
        return [SystemSettingResponse.model_validate(s) for s in settings]

    async def get_setting(self, key: str) -> SystemSettingResponse:
        """Return a single setting by key."""
        result = await self._db.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting is None:
            raise NotFoundError(f"Setting '{key}' not found.")
        return SystemSettingResponse.model_validate(setting)

    async def update_setting(
        self,
        key: str,
        value: str,
        *,
        admin_id: uuid.UUID,
    ) -> SystemSettingResponse:
        """Update the value of a system setting."""
        result = await self._db.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting is None:
            raise NotFoundError(f"Setting '{key}' not found.")
        setting.value = value
        setting.updated_by = admin_id
        self._db.add(setting)
        await self._db.flush()
        await self._db.commit()
        await self._db.refresh(setting)
        return SystemSettingResponse.model_validate(setting)
