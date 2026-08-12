"""
app/schemas/interviewer.py
===========================
Pydantic v2 schemas for Interviewer API endpoints.

SECURITY NOTES:
- Interviewer can only see exams they created (enforced at service layer).
- Candidate data visible only for exams the interviewer owns.
- Score fields in leaderboard are server-computed — never from client.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InterviewerExamSummary(BaseModel):
    """Summary of an exam created by this interviewer."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None = None
    status: str
    duration_minutes: int | None = None
    scheduled_at: datetime | None = None
    created_at: datetime
    total_questions: int = 0
    total_candidates: int = 0
    total_submissions: int = 0


class InterviewerExamListResponse(BaseModel):
    """Paginated list of exams for an interviewer."""

    items: list[InterviewerExamSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class InterviewerCandidateEntry(BaseModel):
    """
    A candidate assigned to one of the interviewer's exams.
    Shows assignment info and attempt status.
    """

    model_config = ConfigDict(from_attributes=True)

    candidate_id: uuid.UUID
    email: str
    exam_id: uuid.UUID
    exam_title: str
    assigned_at: datetime

    # Attempt info
    attempt_status: str | None = None  # None if not started
    submitted_at: datetime | None = None

    # Result info (None if not yet evaluated)
    score: float | None = None
    percentage: float | None = None
    result_status: str | None = None


class InterviewerCandidateListResponse(BaseModel):
    """Paginated candidate list for an interviewer's exams."""

    items: list[InterviewerCandidateEntry]
    total: int
    page: int
    page_size: int
    total_pages: int


class LeaderboardEntry(BaseModel):
    """A single leaderboard row for a completed exam."""

    rank: int
    candidate_id: uuid.UUID
    email: str
    score: float
    total_marks: float
    percentage: float
    correct_count: int
    total_questions: int
    submitted_at: datetime | None = None


class LeaderboardResponse(BaseModel):
    """Leaderboard for a specific exam."""

    exam_id: uuid.UUID
    exam_title: str
    entries: list[LeaderboardEntry]
    total_candidates: int


class InterviewerProfileResponse(BaseModel):
    """Interviewer's own profile."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime | None = None
    last_login_at: datetime | None = None
