"""
app/schemas/user.py
===================
Pydantic v2 user-related schemas.

These schemas are used internally (between service layers) and
for responses. The `UserPublic` schema is the safe representation
returned to API clients — it never includes password_hash.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants import RoleName


class UserPublic(BaseModel):
    """
    Safe public representation of a user.
    Never includes password_hash or internal secrets.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime | None = None
    last_login_at: datetime | None = None


class UserCreate(BaseModel):
    """
    Internal schema for creating a new user record.
    Used only within the service/repository layer.
    NOT exposed via API.
    """

    model_config = ConfigDict(extra="forbid")

    email: str = Field(..., max_length=254)
    password_hash: str = Field(..., description="Pre-computed bcrypt hash.")
    role_id: uuid.UUID
