"""
app/schemas/proctoring_warning.py
===================================
Pydantic v2 schemas for proctoring warnings.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import PAGINATION_DEFAULT_PAGE, PAGINATION_DEFAULT_PAGE_SIZE, PAGINATION_MAX_PAGE_SIZE

# Allowed violation types — enforce at schema layer to prevent junk data.
VIOLATION_TYPES = frozenset({
    "TAB_SWITCH",
    "FACE_NOT_DETECTED",
    "MULTIPLE_FACES",
    "COPY_PASTE",
    "FULLSCREEN_EXIT",
    "AUDIO_DETECTED",
    "SUSPICIOUS_GAZE",
    "OTHER",
})

SEVERITY_LEVELS = frozenset({"LOW", "MEDIUM", "HIGH", "CRITICAL"})


class WarningCreate(BaseModel):
    """
    Request body for logging a proctoring warning.
    Sent by the frontend proctoring client during an active attempt.
    """

    model_config = ConfigDict(extra="forbid")

    violation_type: str = Field(
        ...,
        description=f"One of: {', '.join(sorted(VIOLATION_TYPES))}",
    )
    severity: str = Field(
        default="LOW",
        description="LOW | MEDIUM | HIGH | CRITICAL",
    )
    description: str | None = Field(None, max_length=500)
    # Metadata: browser info, confidence score, etc. Never sensitive PII.
    metadata: dict[str, Any] | None = None


class WarningResponse(BaseModel):
    """Public representation of a proctoring warning."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    attempt_id: uuid.UUID
    candidate_id: uuid.UUID
    violation_type: str
    severity: str
    description: str | None = None
    created_at: datetime


class WarningListResponse(BaseModel):
    """Paginated warning list."""

    items: list[WarningResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class WarningSummary(BaseModel):
    """Summary of proctoring warnings for an attempt."""

    attempt_id: uuid.UUID
    total_warnings: int
    low_count: int
    medium_count: int
    high_count: int
    critical_count: int
