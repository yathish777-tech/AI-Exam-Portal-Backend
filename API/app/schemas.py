from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ExamBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    duration_minutes: int = Field(default=30, ge=1)


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None, ge=1)


class ExamOut(ExamBase):
    id: UUID
    total_marks: int
    status: str
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublishExamRequest(BaseModel):
    published: bool = True


class ScheduleExamRequest(BaseModel):
    scheduled_at: datetime


class QuestionBase(BaseModel):
    question_text: str = Field(..., min_length=5, max_length=1000)
    options: List[str] = Field(..., min_items=2, max_items=6)
    correct_option: str = Field(..., min_length=1)
    marks: int = Field(default=1, ge=1)

    @field_validator("correct_option")
    @classmethod
    def validate_correct_option(cls, value: str):
        if value not in {"A", "B", "C", "D", "E", "F"}:
            raise ValueError("Correct option must be one of A, B, C, D, E, F")
        return value


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(default=None, min_length=5, max_length=1000)
    options: Optional[List[str]] = Field(default=None, min_items=2, max_items=6)
    correct_option: Optional[str] = Field(default=None, min_length=1)
    marks: Optional[int] = Field(default=None, ge=1)


class QuestionOut(QuestionBase):
    id: UUID
    exam_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: str = Field(..., min_length=5, max_length=255)


class CandidateCreate(CandidateBase):
    pass


class CandidateOut(CandidateBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class AssignCandidateRequest(BaseModel):
    candidate_id: UUID


class StartExamRequest(BaseModel):
    exam_id: UUID
    candidate_id: UUID


class SaveAnswerRequest(BaseModel):
    question_id: UUID
    selected_option: str = Field(..., min_length=1)


class AttemptAnswerOut(BaseModel):
    id: UUID
    question_id: UUID
    selected_option: Optional[str]
    is_correct: bool

    model_config = {"from_attributes": True}


class ExamAttemptOut(BaseModel):
    id: UUID
    exam_id: UUID
    candidate_id: UUID
    started_at: datetime
    submitted_at: Optional[datetime]
    status: str
    score: int
    total_marks: int
    answers: List[AttemptAnswerOut] = []

    model_config = {"from_attributes": True}


class ResultOut(BaseModel):
    id: UUID
    exam_id: UUID
    candidate_id: UUID
    exam_attempt_id: UUID
    score: int
    total_marks: int
    percentage: int
    passed: bool
    created_at: datetime

    model_config = {"from_attributes": True}