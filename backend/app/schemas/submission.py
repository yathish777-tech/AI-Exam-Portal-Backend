"""
app/schemas/submission.py
==========================
Pydantic v2 request/response schemas for answer auto-save and submission.

SECURITY NOTES:
- `is_correct` and `score_awarded` are NEVER in request schemas.
  They are computed server-side only.
- `attempt_id` comes from the URL path, not the request body.
- `extra="forbid"` prevents mass-assignment of hidden fields.
- MCQ answer validation: `selected_index` must be an integer >= 0.
- The `answer_data` structure is validated per question_type in the service.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class AnswerSaveRequest(BaseModel):
    """
    Request body for POST /api/v1/attempts/{attempt_id}/answers.

    Auto-saves (upserts) a single answer for one question.
    Can be called repeatedly — each call replaces the previous answer
    for that question using PostgreSQL ON CONFLICT DO UPDATE.

    SECURITY: `is_correct` and `score_awarded` are NOT accepted here.
    """

    model_config = ConfigDict(extra="forbid")

    question_id: uuid.UUID = Field(
        ...,
        description="UUID of the question being answered.",
    )

    answer_data: dict[str, Any] = Field(
        ...,
        description=(
            "Answer payload. Structure depends on question type:\n"
            "  MCQ:          {\"selected_index\": 0}\n"
            "  SHORT_ANSWER: {\"text\": \"Answer text...\"}\n"
            "  CODING:       {\"code\": \"def foo(): ...\", \"language\": \"python\"}\n"
            "  FILE:         Not supported via this endpoint.\n"
        ),
    )


class SubmitRequest(BaseModel):
    """
    Request body for POST /api/v1/attempts/{attempt_id}/submit.

    The body is intentionally minimal — the submission uses whatever answers
    were already auto-saved. An optional `answers` list can be provided for
    a final bulk-save before submitting.
    """

    model_config = ConfigDict(extra="forbid")

    # Optional: last-chance answers before submitting.
    # Each entry is processed as an AnswerSaveRequest.
    answers: list[AnswerSaveRequest] = Field(
        default_factory=list,
        description="Optional final answers to save before submitting.",
    )


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class AnswerSaveResponse(BaseModel):
    """Response confirming an answer was saved/updated."""

    model_config = ConfigDict(extra="forbid")

    question_id: uuid.UUID
    saved: bool = True
    message: str = "Answer saved."


class SubmissionItemResponse(BaseModel):
    """
    Individual answer in a result view.

    SECURITY: `is_correct` and `score_awarded` are included here because
    this schema is used AFTER submission (in results), not during an attempt.
    The service must only return this after the attempt is SUBMITTED.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    question_id: uuid.UUID
    answer_data: dict[str, Any] | None

    # Set by server evaluation — never by client.
    is_correct: bool | None
    score_awarded: float | None
