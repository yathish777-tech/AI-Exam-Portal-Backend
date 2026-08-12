"""
app/schemas/analytics.py
==========================
Pydantic v2 schemas for analytics/dashboard endpoints.

ADMIN and INTERVIEWER facing. All fields are server-computed aggregates.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlatformStats(BaseModel):
    """
    High-level platform statistics for the Admin dashboard.
    All values are server-computed — never accepted from client.
    """

    total_users: int
    total_admins: int
    total_interviewers: int
    total_candidates: int
    active_users: int
    inactive_users: int

    total_exams: int
    draft_exams: int
    published_exams: int
    completed_exams: int

    total_attempts: int
    submitted_attempts: int
    in_progress_attempts: int

    total_results: int
    evaluated_results: int
    pending_evaluation_results: int

    total_proctoring_warnings: int


class ExamAnalytics(BaseModel):
    """Per-exam analytics for an interviewer or admin."""

    exam_id: uuid.UUID
    exam_title: str
    exam_status: str

    total_candidates: int
    started_attempts: int
    submitted_attempts: int
    abandoned_attempts: int
    completion_rate: float  # submitted / total_candidates * 100

    average_score: float | None = None
    highest_score: float | None = None
    lowest_score: float | None = None
    average_percentage: float | None = None

    evaluated_results: int
    pending_evaluation_results: int
    total_proctoring_warnings: int


class CandidateAnalytics(BaseModel):
    """Per-candidate analytics visible to admins."""

    candidate_id: uuid.UUID
    email: str

    total_exams_assigned: int
    total_exams_attempted: int
    total_exams_submitted: int

    average_score: float | None = None
    average_percentage: float | None = None
    highest_percentage: float | None = None

    total_proctoring_warnings: int
    high_severity_warnings: int


class AnalyticsPeriodFilter(BaseModel):
    """Optional date range filter for analytics queries."""

    model_config = ConfigDict(extra="forbid")

    from_date: datetime | None = None
    to_date: datetime | None = None
