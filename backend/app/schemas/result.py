"""
app/schemas/result.py
======================
Pydantic v2 response schemas for exam result endpoints.

SECURITY NOTES:
- All score fields are read-only — set only by server-side evaluation.
- Candidates can only see their own result.
- Interviewers see results for their exam's candidates only.
- The detailed question breakdown (is_correct per question) is included
  only when the exam config allows showing results immediately, or after
  the exam window has closed (enforced at service layer).
- `extra="forbid"` prevents unexpected fields from leaking.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.submission import SubmissionItemResponse


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class ResultResponse(BaseModel):
    """
    Full result for a completed exam attempt.

    Returned to the candidate who owns the attempt, or to an interviewer/admin
    for their exam's results.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    attempt_id: uuid.UUID
    candidate_id: uuid.UUID
    exam_id: uuid.UUID

    # Score breakdown — all set by server evaluation only.
    total_questions: int
    attempted_count: int
    correct_count: int
    incorrect_count: int
    total_marks: float
    score: float
    percentage: float

    # EVALUATED | PENDING_EVALUATION
    status: str

    created_at: datetime
    updated_at: datetime

    # Optional: per-question answer breakdown.
    # Included only when explicitly requested and allowed by exam config.
    answers: list[SubmissionItemResponse] = Field(default_factory=list)


class ResultSummaryItem(BaseModel):
    """
    Compact result item for exam-level result listing (interviewer/admin view).

    Does not include per-question answer breakdown.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    attempt_id: uuid.UUID
    candidate_id: uuid.UUID

    # Candidate email included for display.
    candidate_email: str = ""

    total_marks: float
    score: float
    percentage: float
    status: str
    created_at: datetime


class ExamResultsListResponse(BaseModel):
    """Paginated list of results for an exam (interviewer/admin view)."""

    model_config = ConfigDict(extra="forbid")

    items: list[ResultSummaryItem]
    total: int
    exam_id: uuid.UUID
