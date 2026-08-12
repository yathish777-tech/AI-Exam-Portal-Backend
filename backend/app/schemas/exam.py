"""
app/schemas/exam.py
===================
Pydantic v2 request/response schemas for exam management endpoints.

SECURITY NOTES:
- `extra="forbid"` on all request schemas prevents mass-assignment.
- Protected fields (`created_by`, `status`) are NEVER in request schemas.
- `status` changes happen only via dedicated lifecycle endpoints
  (publish, schedule) — never via PATCH.
- Response schemas include `created_by` as a UUID for audit display,
  but never expose internal DB metadata or other users' data.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.constants import ExamStatus


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class ExamCreate(BaseModel):
    """Request body for POST /api/v1/exams."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Exam title.",
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
        description="Optional exam description.",
    )
    duration_minutes: int | None = Field(
        default=None,
        ge=1,
        le=600,
        description="Exam duration in minutes (1–600). None = no time limit.",
    )
    scheduled_at: datetime | None = Field(
        default=None,
        description="Optional scheduled start time (UTC). Must be in the future.",
    )
    config: dict[str, Any] | None = Field(
        default=None,
        description="Optional exam configuration (e.g. shuffle_questions: true).",
    )

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_at_must_be_future(cls, v: datetime | None) -> datetime | None:
        if v is not None:
            from datetime import timezone
            now = datetime.now(timezone.utc)
            # Make scheduled_at timezone-aware if naive
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v <= now:
                raise ValueError("scheduled_at must be a future datetime.")
        return v


class ExamUpdate(BaseModel):
    """
    Request body for PATCH /api/v1/exams/{exam_id}.

    All fields optional. Status is NOT included — use lifecycle endpoints.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )
    description: str | None = Field(default=None, max_length=5000)
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    scheduled_at: datetime | None = Field(default=None)
    config: dict[str, Any] | None = Field(default=None)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "ExamUpdate":
        if all(
            v is None
            for v in [
                self.title,
                self.description,
                self.duration_minutes,
                self.scheduled_at,
                self.config,
            ]
        ):
            raise ValueError("At least one field must be provided for update.")
        return self


class ExamScheduleRequest(BaseModel):
    """Request body for POST /api/v1/exams/{exam_id}/schedule."""

    model_config = ConfigDict(extra="forbid")

    scheduled_at: datetime = Field(
        ...,
        description="Scheduled start time (UTC). Must be in the future.",
    )

    @field_validator("scheduled_at")
    @classmethod
    def must_be_future(cls, v: datetime) -> datetime:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= now:
            raise ValueError("scheduled_at must be a future datetime.")
        return v


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class ExamResponse(BaseModel):
    """Exam representation returned to authenticated users."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    created_by: uuid.UUID
    title: str
    description: str | None
    duration_minutes: int | None
    status: str
    scheduled_at: datetime | None
    config: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    # Computed fields
    question_count: int = Field(default=0, description="Number of questions in exam.")

    @classmethod
    def from_orm_with_count(cls, exam: Any, question_count: int = 0) -> "ExamResponse":
        """Build response from ORM object + computed question count."""
        return cls(
            id=exam.id,
            created_by=exam.created_by,
            title=exam.title,
            description=exam.description,
            duration_minutes=exam.duration_minutes,
            status=exam.status,
            scheduled_at=exam.scheduled_at,
            config=exam.config,
            created_at=exam.created_at,
            updated_at=exam.updated_at,
            question_count=question_count,
        )


class ExamListItem(BaseModel):
    """Compact exam item for list responses."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    title: str
    status: str
    duration_minutes: int | None
    scheduled_at: datetime | None
    created_at: datetime
    question_count: int = 0


class ExamCandidateView(BaseModel):
    """Exam info returned to a candidate on their upcoming/completed exam list."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    title: str
    description: str | None
    duration_minutes: int | None
    status: str
    scheduled_at: datetime | None
    assigned_at: datetime
