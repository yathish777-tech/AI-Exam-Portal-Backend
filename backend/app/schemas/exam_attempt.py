"""
app/schemas/exam_attempt.py
============================
Pydantic v2 request/response schemas for exam attempt endpoints.

SECURITY NOTES:
- Candidates CANNOT set their own attempt status or start time.
- `candidate_id` is always taken from the authenticated user — never
  from the request body.
- Questions returned to candidates during an attempt strip MCQ correct_index.
- `submitted_at` is server-generated on submission.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.question import QuestionCandidateResponse


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class AttemptResponse(BaseModel):
    """
    Exam attempt detail returned to a candidate after starting or retrieving
    an attempt.

    Includes all questions (with correct_index stripped for candidates).
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    exam_id: uuid.UUID
    candidate_id: uuid.UUID
    status: str
    started_at: datetime
    submitted_at: datetime | None

    # Questions included so the candidate can begin answering.
    # Each question has MCQ correct_index stripped (see QuestionCandidateResponse).
    questions: list[QuestionCandidateResponse] = Field(default_factory=list)

    # Duration in minutes (from the exam). None = no time limit.
    duration_minutes: int | None = None

    # Exam title for display.
    exam_title: str = ""


class AttemptListItem(BaseModel):
    """Compact attempt item for list views."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    exam_id: uuid.UUID
    status: str
    started_at: datetime
    submitted_at: datetime | None


class AttemptStartResponse(BaseModel):
    """Response returned when a candidate successfully starts an exam attempt."""

    model_config = ConfigDict(extra="forbid")

    attempt: AttemptResponse
    message: str = "Exam attempt started successfully."
