"""
app/schemas/admin.py
=====================
Pydantic v2 schemas for Admin API endpoints.

SECURITY NOTES:
- Role, status, and ID fields in responses are read-only from server.
- AdminUserUpdate explicitly excludes password and role manipulation
  (those have dedicated endpoints).
- Mass assignment is prevented by extra="forbid" on all request schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants import RoleName


class AdminUserResponse(BaseModel):
    """Full user record as seen by an admin."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime | None = None
    last_login_at: datetime | None = None


class AdminUserListResponse(BaseModel):
    """Paginated list of users for admin view."""

    items: list[AdminUserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminUserUpdate(BaseModel):
    """
    Update a user's active status only.
    Role changes are a separate endpoint to prevent accidental privilege escalation.
    """

    model_config = ConfigDict(extra="forbid")

    is_active: bool


class AdminRoleChangeRequest(BaseModel):
    """
    Change a user's role.
    ADMIN only. Separate from general update to enforce explicit intent.
    """

    model_config = ConfigDict(extra="forbid")

    role: RoleName = Field(..., description="New role: ADMIN | INTERVIEWER | CANDIDATE")


class ActivityLogResponse(BaseModel):
    """Public representation of an activity log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_id: uuid.UUID | None = None
    action: str
    resource_type: str | None = None
    resource_id: uuid.UUID | None = None
    description: str | None = None
    ip_address: str | None = None
    created_at: datetime


class ActivityLogListResponse(BaseModel):
    """Paginated activity log list."""

    items: list[ActivityLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SystemSettingResponse(BaseModel):
    """Public representation of a system setting."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    value: str
    description: str | None = None
    value_type: str
    updated_by: uuid.UUID | None = None
    updated_at: datetime | None = None


class SystemSettingUpdate(BaseModel):
    """Update a system setting's value."""

    model_config = ConfigDict(extra="forbid")

    value: str = Field(..., max_length=2000)


class AdminCreateUserRequest(BaseModel):
    """
    Admin creates a new user with a specific role.
    Used for bulk onboarding of interviewers or pre-registering candidates.
    """

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=10, max_length=128)
    role: RoleName = Field(..., description="ADMIN | INTERVIEWER | CANDIDATE")
