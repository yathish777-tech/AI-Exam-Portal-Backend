"""
app/services/submission_service.py
=====================================
Business logic for auto-saving answers and submitting exams.

SECURITY:
- `is_correct` and `score_awarded` are NEVER accepted from clients.
  They are computed server-side only during `submit_exam()`.
- Ownership verified: candidate must own the attempt.
- Attempt must be IN_PROGRESS for saves or submission.
- Question must belong to the exam (prevents cross-exam answer injection).
- Submission is atomic: answers are evaluated and result is stored in one
  database transaction.
- Double-submission is prevented: submitting an already-SUBMITTED attempt
  raises ConflictError.

CODING/FILE questions: Auto-evaluated as PENDING (no sandboxed executor yet).
MCQ: Evaluated immediately by comparing selected_index to correct_index.
SHORT_ANSWER: Evaluated as PENDING (requires manual/AI review).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AttemptStatus, QuestionType, ResultStatus, SecurityEvent
from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError, ValidationError
from app.core.logging import log_security_event
from app.models.user import User
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.submission_repository import SubmissionRepository
from app.schemas.submission import AnswerSaveRequest, AnswerSaveResponse


class SubmissionService:
    """
    Orchestrates answer auto-save and exam submission + evaluation.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._attempts = AttemptRepository
        self._questions = QuestionRepository
        self._submissions = SubmissionRepository
        self._results = ResultRepository

    # -----------------------------------------------------------------------
    # Auto-save answer
    # -----------------------------------------------------------------------

    async def save_answer(
        self,
        attempt_id: uuid.UUID,
        request: AnswerSaveRequest,
        current_user: User,
        *,
        request_id: str = "",
    ) -> AnswerSaveResponse:
        """
        Auto-save (upsert) a single answer for a question in an attempt.

        Can be called repeatedly — each call replaces the previous answer.
        Uses PostgreSQL ON CONFLICT DO UPDATE (idempotent).

        SECURITY checks:
        1. Attempt exists and belongs to this candidate (IDOR prevention).
        2. Attempt is IN_PROGRESS (not already submitted).
        3. Question belongs to this attempt's exam.
        4. answer_data structure is validated per question_type.
        """
        # 1. Verify attempt ownership
        attempt = await self._attempts.get_by_id_for_candidate(
            self._db, attempt_id, current_user.id
        )
        if attempt is None:
            log_security_event(
                SecurityEvent.IDOR_ATTEMPT,
                request_id=request_id,
                user_id=str(current_user.id),
                ip_address="",
                endpoint=f"/attempts/{attempt_id}/answers",
                success=False,
                detail="Attempt not found or does not belong to user",
            )
            raise NotFoundError(f"Attempt {attempt_id} not found.")

        # 2. Attempt must be IN_PROGRESS
        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise ConflictError(
                f"Cannot save answers to an attempt with status '{attempt.status}'. "
                "The attempt must be in progress."
            )

        # 3. Verify question belongs to this exam
        question = await self._questions.get_by_id_for_exam(
            self._db, request.question_id, attempt.exam_id
        )
        if question is None:
            raise NotFoundError(
                f"Question {request.question_id} does not belong to this exam."
            )

        # 4. Validate answer_data structure
        self._validate_answer_data(
            request.answer_data, question.question_type
        )

        # 5. Upsert the answer
        await self._submissions.upsert_answer(
            self._db,
            attempt_id=attempt_id,
            question_id=request.question_id,
            answer_data=request.answer_data,
        )
        await self._db.commit()

        log_security_event(
            SecurityEvent.ANSWER_SAVED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/attempts/{attempt_id}/answers",
        )

        return AnswerSaveResponse(question_id=request.question_id)

    # -----------------------------------------------------------------------
    # Submit exam
    # -----------------------------------------------------------------------

    async def submit_exam(
        self,
        attempt_id: uuid.UUID,
        final_answers: list[AnswerSaveRequest],
        current_user: User,
        *,
        request_id: str = "",
    ) -> dict:
        """
        Finalize and submit an exam attempt.

        Flow (atomic transaction):
        1. Verify attempt ownership and IN_PROGRESS status.
        2. Save any final answers provided in the submit body.
        3. Evaluate all answers (MCQ auto-graded; others → PENDING).
        4. Compute result totals.
        5. Store ExamResult.
        6. Mark attempt as SUBMITTED with submitted_at timestamp.
        7. Commit.

        SECURITY:
        - Double submission raises ConflictError (409).
        - `score`, `is_correct` are computed server-side — never from client.
        - The entire flow is wrapped in one transaction.
        """
        # 1. Verify ownership and status
        attempt = await self._attempts.get_by_id_for_candidate(
            self._db, attempt_id, current_user.id
        )
        if attempt is None:
            log_security_event(
                SecurityEvent.IDOR_ATTEMPT,
                request_id=request_id,
                user_id=str(current_user.id),
                ip_address="",
                endpoint=f"/attempts/{attempt_id}/submit",
                success=False,
                detail="Attempt not found or does not belong to user",
            )
            raise NotFoundError(f"Attempt {attempt_id} not found.")

        if attempt.status == AttemptStatus.SUBMITTED:
            log_security_event(
                SecurityEvent.EXAM_ALREADY_SUBMITTED,
                request_id=request_id,
                user_id=str(current_user.id),
                ip_address="",
                endpoint=f"/attempts/{attempt_id}/submit",
                success=False,
            )
            raise ConflictError(
                "This exam has already been submitted. "
                "Double submission is not allowed."
            )

        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise ValidationError(
                f"Cannot submit an attempt with status '{attempt.status}'."
            )

        # 2. Save any final answers provided with the submit request
        if final_answers:
            questions = await self._questions.list_by_exam(self._db, attempt.exam_id)
            question_map = {q.id: q for q in questions}

            for answer_req in final_answers:
                if answer_req.question_id not in question_map:
                    raise NotFoundError(
                        f"Question {answer_req.question_id} does not belong to this exam."
                    )
                question = question_map[answer_req.question_id]
                self._validate_answer_data(answer_req.answer_data, question.question_type)
                await self._submissions.upsert_answer(
                    self._db,
                    attempt_id=attempt_id,
                    question_id=answer_req.question_id,
                    answer_data=answer_req.answer_data,
                )

        # 3. Evaluate all answers
        questions = await self._questions.list_by_exam(self._db, attempt.exam_id)
        submissions = await self._submissions.list_by_attempt(self._db, attempt_id)

        question_map = {q.id: q for q in questions}
        submission_map = {s.question_id: s for s in submissions}

        has_non_mcq = False
        total_marks = 0.0
        score = 0.0
        correct_count = 0
        incorrect_count = 0
        attempted_count = len(submissions)

        for question in questions:
            total_marks += float(question.marks)
            submission = submission_map.get(question.id)

            if submission is None:
                continue  # Unattempted question — no points

            q_type = question.question_type
            if q_type == QuestionType.MCQ:
                is_correct, marks_awarded = self._evaluate_mcq(
                    submission.answer_data, question.options, float(question.marks)
                )
                await self._submissions.set_evaluation(
                    self._db, submission.id, is_correct, marks_awarded
                )
                if is_correct:
                    score += marks_awarded
                    correct_count += 1
                else:
                    incorrect_count += 1
            else:
                # SHORT_ANSWER, CODING, FILE — requires manual/AI evaluation
                has_non_mcq = True
                await self._submissions.set_evaluation(
                    self._db, submission.id, is_correct=False, score_awarded=0.0
                )

        result_status = (
            ResultStatus.PENDING_EVALUATION if has_non_mcq
            else ResultStatus.EVALUATED
        )
        percentage = (score / total_marks * 100) if total_marks > 0 else 0.0

        # 4. Store result
        exam_result = await self._results.create_result(
            self._db,
            attempt_id=attempt_id,
            candidate_id=current_user.id,
            exam_id=attempt.exam_id,
            total_questions=len(questions),
            attempted_count=attempted_count,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            total_marks=total_marks,
            score=score,
            percentage=percentage,
            status=result_status.value,
        )

        # 5. Mark attempt as SUBMITTED
        attempt.status = AttemptStatus.SUBMITTED
        attempt.submitted_at = datetime.now(timezone.utc)

        # 6. Commit atomically
        await self._db.commit()
        await self._db.refresh(exam_result)

        log_security_event(
            SecurityEvent.EXAM_SUBMITTED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/attempts/{attempt_id}/submit",
        )

        log_security_event(
            SecurityEvent.RESULT_CREATED,
            request_id=request_id,
            user_id=str(current_user.id),
            ip_address="",
            endpoint=f"/attempts/{attempt_id}/submit",
        )

        return {
            "attempt_id": str(attempt_id),
            "result_id": str(exam_result.id),
            "score": float(exam_result.score),
            "total_marks": float(exam_result.total_marks),
            "percentage": float(exam_result.percentage),
            "status": exam_result.status,
            "message": (
                "Exam submitted successfully. Results are pending manual evaluation."
                if has_non_mcq
                else "Exam submitted and evaluated successfully."
            ),
        }

    # -----------------------------------------------------------------------
    # Private evaluation helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _evaluate_mcq(
        answer_data: dict[str, Any] | None,
        options: dict[str, Any] | None,
        marks: float,
    ) -> tuple[bool, float]:
        """
        Evaluate an MCQ answer server-side.

        Returns (is_correct, score_awarded).
        SECURITY: `correct_index` comes from the server-stored `options` JSONB,
        never from client-submitted data.
        """
        if not answer_data or options is None:
            return False, 0.0

        selected = answer_data.get("selected_index")
        correct = options.get("correct_index")

        if selected is None or correct is None:
            return False, 0.0

        try:
            is_correct = int(selected) == int(correct)
        except (TypeError, ValueError):
            return False, 0.0

        return is_correct, marks if is_correct else 0.0

    @staticmethod
    def _validate_answer_data(
        answer_data: dict[str, Any],
        question_type: str,
    ) -> None:
        """
        Validate that answer_data has the correct structure for the question type.

        SECURITY: Rejects unexpected fields and ensures type safety.
        """
        if question_type == QuestionType.MCQ:
            if set(answer_data) != {"selected_index"}:
                raise ValidationError("MCQ answer may only include 'selected_index'.")
            if "selected_index" not in answer_data:
                raise ValidationError(
                    "MCQ answer must include 'selected_index' (integer)."
                )
            try:
                idx = int(answer_data["selected_index"])
                if idx < 0:
                    raise ValidationError("selected_index must be >= 0.")
            except (TypeError, ValueError):
                raise ValidationError("selected_index must be an integer.")

        elif question_type == QuestionType.SHORT_ANSWER:
            if set(answer_data) != {"text"}:
                raise ValidationError("SHORT_ANSWER answer may only include 'text'.")
            if "text" not in answer_data:
                raise ValidationError(
                    "SHORT_ANSWER must include 'text' field."
                )
            if not isinstance(answer_data["text"], str):
                raise ValidationError("SHORT_ANSWER 'text' must be a string.")

        elif question_type == QuestionType.CODING:
            if not set(answer_data).issubset({"code", "language"}):
                raise ValidationError("CODING answer may only include 'code' and 'language'.")
            # Basic validation — full sandboxed evaluation is a future phase
            if "code" not in answer_data:
                raise ValidationError(
                    "CODING answer must include 'code' field."
                )
            if not isinstance(answer_data["code"], str):
                raise ValidationError("CODING 'code' must be a string.")
            if "language" in answer_data and not isinstance(answer_data["language"], str):
                raise ValidationError("CODING 'language' must be a string.")
            # NEVER execute the code - it goes to PENDING evaluation
        elif question_type == QuestionType.FILE:
            if set(answer_data) != {"file_path"}:
                raise ValidationError("FILE answer must include only 'file_path'.")
            if not isinstance(answer_data["file_path"], str) or not answer_data["file_path"]:
                raise ValidationError("FILE 'file_path' must be a non-empty string.")
        else:
            raise ValidationError(f"Unsupported question type '{question_type}'.")
