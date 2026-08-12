"""
app/schemas/exam_candidate.py
==============================
Pydantic v2 schemas for candidate assignment endpoints.

SECURITY NOTES:
- `candidate_ids` is the ONLY accepted field — no other user fields.
- Candidates cannot assign themselves (enforced at service layer).
- Response includes candidate email for display — no password_hash or
  other sensitive fields.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class CandidateAssignRequest(BaseModel):
    """
    Request body for POST /api/v1/exams/{exam_id}/candidates.

    Accepts a list of candidate UUIDs to assign to the exam.
    """

    model_config = ConfigDict(extra="forbid")

    candidate_ids: list[uuid.UUID] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="List of candidate user UUIDs to assign.",
    )


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class CandidateAssignmentResponse(BaseModel):
    """Response after assigning candidates to an exam."""

    model_config = ConfigDict(extra="forbid")

    assigned_count: int = Field(description="Number of new candidates assigned.")
    skipped_count: int = Field(
        description="Number of candidates skipped (already assigned or invalid)."
    )
    message: str


class CandidateItem(BaseModel):
    """
    A single candidate in the exam candidates list.

    SECURITY: Only email and UUID are returned — never password_hash.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    candidate_id: uuid.UUID
    email: str
    assigned_at: datetime
    assigned_by: uuid.UUID | None


class CandidateListResponse(BaseModel):
    """Paginated list of candidates assigned to an exam."""

    model_config = ConfigDict(extra="forbid")

    items: list[CandidateItem]
    total: int
