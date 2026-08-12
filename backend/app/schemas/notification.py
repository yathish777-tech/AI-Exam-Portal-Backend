"""
app/schemas/notification.py
=============================
Pydantic v2 schemas for notifications.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    """Public representation of a notification."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    notification_type: str
    title: str
    message: str
    reference_id: uuid.UUID | None = None
    reference_type: str | None = None
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Paginated notification list."""

    model_config = ConfigDict(from_attributes=True)

    items: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
    total_pages: int


class MarkReadRequest(BaseModel):
    """Request body for marking specific notifications as read."""

    model_config = ConfigDict(extra="forbid")

    notification_ids: list[uuid.UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of notification IDs to mark as read.",
    )


class UnreadCountResponse(BaseModel):
    """Unread notification count."""

    unread_count: int
