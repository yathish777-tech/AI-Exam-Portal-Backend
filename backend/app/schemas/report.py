"""
app/schemas/report.py
======================
Pydantic v2 schemas for report generation endpoints.

Reports are read-only server-computed summaries for admin/interviewer use.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExamReportEntry(BaseModel):
    """One candidate's result row in an exam report."""

    model_config = ConfigDict(from_attributes=True)

    rank: int
    candidate_id: uuid.UUID
    email: str
    attempt_status: str
    score: float | None = None
    total_marks: float | None = None
    percentage: float | None = None
    correct_count: int | None = None
    total_questions: int | None = None
    result_status: str | None = None
    started_at: datetime | None = None
    submitted_at: datetime | None = None
    proctoring_warnings: int = 0


class ExamReport(BaseModel):
    """Full report for a single exam."""

    exam_id: uuid.UUID
    exam_title: str
    exam_status: str
    duration_minutes: int | None = None
    scheduled_at: datetime | None = None
    created_at: datetime

    total_candidates: int
    submitted_count: int
    average_percentage: float | None = None
    pass_count: int = 0  # percentage >= pass threshold
    fail_count: int = 0

    entries: list[ExamReportEntry]
    generated_at: datetime


class CandidateReportEntry(BaseModel):
    """One exam row in a candidate's personal report."""

    model_config = ConfigDict(from_attributes=True)

    exam_id: uuid.UUID
    exam_title: str
    attempt_status: str | None = None
    score: float | None = None
    total_marks: float | None = None
    percentage: float | None = None
    result_status: str | None = None
    submitted_at: datetime | None = None
    proctoring_warnings: int = 0


class CandidateReport(BaseModel):
    """Full performance report for a single candidate."""

    candidate_id: uuid.UUID
    email: str

    total_exams_assigned: int
    total_exams_submitted: int
    average_percentage: float | None = None

    entries: list[CandidateReportEntry]
    generated_at: datetime
