"""
app/schemas/question.py
=======================
Pydantic v2 request/response schemas for question management endpoints.

SECURITY NOTES:
- MCQ `options.correct_index` is accepted in CREATE/UPDATE (interviewer only).
- MCQ `options.correct_index` is STRIPPED from candidate-facing responses.
  Candidates must never see the correct answer before or during an attempt.
- `exam_id` is NOT in request body for PATCH/DELETE — it comes from the URL
  and is verified against the authenticated owner in the service layer.
- Negative marks are rejected by validator.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.constants import QuestionType


# ---------------------------------------------------------------------------
# MCQ Options sub-schema
# ---------------------------------------------------------------------------

class MCQOptions(BaseModel):
    """Structure for MCQ question options."""

    model_config = ConfigDict(extra="forbid")

    choices: list[str] = Field(
        ...,
        min_length=2,
        max_length=6,
        description="2–6 answer choices.",
    )
    correct_index: int = Field(
        ...,
        ge=0,
        description="0-based index of the correct choice.",
    )

    @model_validator(mode="after")
    def correct_index_in_bounds(self) -> "MCQOptions":
        if self.correct_index >= len(self.choices):
            raise ValueError(
                f"correct_index ({self.correct_index}) is out of range "
                f"for {len(self.choices)} choices."
            )
        return self


class MCQOptionsCandidate(BaseModel):
    """MCQ options returned to candidates — correct_index is stripped."""

    model_config = ConfigDict(extra="forbid")

    choices: list[str]
    # correct_index intentionally omitted


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class QuestionCreate(BaseModel):
    """Request body for POST /api/v1/exams/{exam_id}/questions."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question_type: QuestionType = Field(
        ...,
        description="Type: MCQ | SHORT_ANSWER | CODING | FILE",
    )
    content: str = Field(
        ...,
        min_length=5,
        max_length=10000,
        description="Question text or prompt.",
    )
    marks: float = Field(
        default=1.0,
        gt=0,
        le=1000,
        description="Points for a correct answer. Must be > 0.",
    )
    order_number: int | None = Field(
        default=None,
        ge=1,
        description="Display order (1-based). Auto-assigned if omitted.",
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description="MCQ: {choices: [...], correct_index: 0}. Required for MCQ.",
    )

    @model_validator(mode="after")
    def validate_mcq_options(self) -> "QuestionCreate":
        if self.question_type == QuestionType.MCQ:
            if not self.options:
                raise ValueError("options is required for MCQ questions.")
            # Validate structure via MCQOptions
            MCQOptions(**self.options)
        return self


class QuestionUpdate(BaseModel):
    """Request body for PATCH /api/v1/questions/{question_id}."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    content: str | None = Field(default=None, min_length=5, max_length=10000)
    marks: float | None = Field(default=None, gt=0, le=1000)
    order_number: int | None = Field(default=None, ge=1)
    options: dict[str, Any] | None = Field(default=None)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "QuestionUpdate":
        if all(v is None for v in [self.content, self.marks, self.order_number, self.options]):
            raise ValueError("At least one field must be provided for update.")
        return self


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class QuestionResponse(BaseModel):
    """Question response for interviewers/admins (includes correct answer)."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    exam_id: uuid.UUID
    question_type: str
    content: str
    marks: float
    order_number: int
    options: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class QuestionCandidateResponse(BaseModel):
    """
    Question response for candidates during an exam attempt.

    SECURITY: `correct_index` is STRIPPED from MCQ options.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    exam_id: uuid.UUID
    question_type: str
    content: str
    marks: float
    order_number: int
    # MCQ: only choices are returned; correct_index is omitted.
    options: dict[str, Any] | None

    @classmethod
    def from_question(cls, question: Any) -> "QuestionCandidateResponse":
        """Strip correct_index from MCQ options before returning to candidate."""
        options = None
        if question.options:
            if question.question_type == QuestionType.MCQ:
                # Return only choices — never correct_index
                options = {"choices": question.options.get("choices", [])}
            else:
                options = question.options
        return cls(
            id=question.id,
            exam_id=question.exam_id,
            question_type=question.question_type,
            content=question.content,
            marks=question.marks,
            order_number=question.order_number,
            options=options,
        )
