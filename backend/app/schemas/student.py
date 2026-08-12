"""
app/schemas/student.py
=======================
Pydantic v2 schemas for Student (CANDIDATE) API endpoints.

SECURITY NOTES:
- All candidate_id fields in responses are derived from authenticated user.
- Score and result fields are server-computed — never accepted from client.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudentExamSummary(BaseModel):
    """
    Summary of an exam as seen by a candidate on their dashboard.
    Includes assignment context and attempt status if started.
    """

    model_config = ConfigDict(from_attributes=True)

    exam_id: uuid.UUID
    title: str
    description: str | None = None
    duration_minutes: int | None = None
    status: str  # exam status: PUBLISHED | SCHEDULED | COMPLETED
    scheduled_at: datetime | None = None
    assigned_at: datetime

    # Attempt info (null if not yet started)
    attempt_id: uuid.UUID | None = None
    attempt_status: str | None = None  # IN_PROGRESS | SUBMITTED | ABANDONED
    started_at: datetime | None = None
    submitted_at: datetime | None = None


class StudentExamListResponse(BaseModel):
    """Paginated list of assigned exams for a student."""

    items: list[StudentExamSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class StudentResultSummary(BaseModel):
    """
    Summary of a single exam result for the student's history view.
    Score and percentage are read-only server-computed fields.
    """

    model_config = ConfigDict(from_attributes=True)

    result_id: uuid.UUID
    exam_id: uuid.UUID
    exam_title: str
    attempt_id: uuid.UUID
    score: float
    total_marks: float
    percentage: float
    total_questions: int
    attempted_count: int
    correct_count: int
    status: str  # EVALUATED | PENDING_EVALUATION
    submitted_at: datetime | None = None
    created_at: datetime


class StudentResultListResponse(BaseModel):
    """Paginated list of exam results for a student."""

    items: list[StudentResultSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class StudentProfileResponse(BaseModel):
    """Student's own profile data."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime | None = None
    last_login_at: datetime | None = None
