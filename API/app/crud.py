from datetime import datetime
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app import models, schemas


def create_exam(db: Session, exam: schemas.ExamCreate) -> models.Exam:
    db_exam = models.Exam(
        title=exam.title,
        description=exam.description,
        duration_minutes=exam.duration_minutes,
        total_marks=0,
        status="draft",
    )
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam


def get_exams(db: Session) -> List[models.Exam]:
    return db.query(models.Exam).order_by(models.Exam.created_at.desc()).all()


def get_exam(db: Session, exam_id: int) -> models.Exam | None:
    return db.query(models.Exam).filter(models.Exam.id == exam_id).first()


def update_exam(db: Session, exam_id: int, exam: schemas.ExamUpdate) -> models.Exam | None:
    db_exam = get_exam(db, exam_id)
    if not db_exam:
        return None

    for field, value in exam.model_dump(exclude_unset=True).items():
        setattr(db_exam, field, value)

    db.commit()
    db.refresh(db_exam)
    return db_exam


def delete_exam(db: Session, exam_id: int) -> bool:
    db_exam = get_exam(db, exam_id)
    if not db_exam:
        return False
    db.delete(db_exam)
    db.commit()
    return True


def publish_exam(db: Session, exam_id: int) -> models.Exam | None:
    db_exam = get_exam(db, exam_id)
    if not db_exam:
        return None
    db_exam.status = "published"
    db_exam.published_at = datetime.utcnow()
    db.commit()
    db.refresh(db_exam)
    return db_exam


def schedule_exam(db: Session, exam_id: int, scheduled_at: datetime) -> models.Exam | None:
    db_exam = get_exam(db, exam_id)
    if not db_exam:
        return None
    db_exam.status = "scheduled"
    db_exam.scheduled_at = scheduled_at
    db.commit()
    db.refresh(db_exam)
    return db_exam


def create_question(db: Session, exam_id: int, question: schemas.QuestionCreate) -> models.Question:
    exam = get_exam(db, exam_id)
    if not exam:
        raise ValueError("Exam not found")

    db_question = models.Question(
        exam_id=exam_id,
        question_text=question.question_text,
        options=question.options,
        correct_option=question.correct_option,
        marks=question.marks,
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    exam.total_marks += question.marks
    db.commit()
    return db_question


def get_questions(db: Session, exam_id: int) -> List[models.Question]:
    return db.query(models.Question).filter(models.Question.exam_id == exam_id).all()


def get_question(db: Session, question_id: int) -> models.Question | None:
    return db.query(models.Question).filter(models.Question.id == question_id).first()


def update_question(db: Session, question_id: int, question: schemas.QuestionUpdate) -> models.Question | None:
    db_question = get_question(db, question_id)
    if not db_question:
        return None

    data = question.model_dump(exclude_unset=True)
    if "marks" in data and data["marks"] != db_question.marks:
        delta = data["marks"] - db_question.marks
        db_question.exam.total_marks += delta

    for field, value in data.items():
        setattr(db_question, field, value)

    db.commit()
    db.refresh(db_question)
    return db_question


def delete_question(db: Session, question_id: int) -> bool:
    db_question = get_question(db, question_id)
    if not db_question:
        return False
    db_question.exam.total_marks -= db_question.marks
    db.delete(db_question)
    db.commit()
    return True


def create_candidate(db: Session, candidate: schemas.CandidateCreate) -> models.Candidate:
    db_candidate = models.Candidate(full_name=candidate.full_name, email=candidate.email)
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


def get_candidate(db: Session, candidate_id: int) -> models.Candidate | None:
    return db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()


def assign_candidate(db: Session, exam_id: int, candidate_id: int) -> models.ExamCandidate:
    exam = get_exam(db, exam_id)
    candidate = get_candidate(db, candidate_id)
    if not exam or not candidate:
        raise ValueError("Exam or candidate not found")

    existing = (
        db.query(models.ExamCandidate)
        .filter(and_(models.ExamCandidate.exam_id == exam_id, models.ExamCandidate.candidate_id == candidate_id))
        .first()
    )
    if existing:
        return existing

    assignment = models.ExamCandidate(exam_id=exam_id, candidate_id=candidate_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def remove_candidate(db: Session, exam_id: int, candidate_id: int) -> bool:
    assignment = (
        db.query(models.ExamCandidate)
        .filter(and_(models.ExamCandidate.exam_id == exam_id, models.ExamCandidate.candidate_id == candidate_id))
        .first()
    )
    if not assignment:
        return False
    db.delete(assignment)
    db.commit()
    return True


def get_assigned_candidates(db: Session, exam_id: int) -> List[models.Candidate]:
    assignments = (
        db.query(models.ExamCandidate)
        .filter(models.ExamCandidate.exam_id == exam_id)
        .all()
    )
    return [assignment.candidate for assignment in assignments]


def start_exam(db: Session, exam_id: int, candidate_id: int) -> models.ExamAttempt:
    exam = get_exam(db, exam_id)
    candidate = get_candidate(db, candidate_id)
    if not exam or not candidate:
        raise ValueError("Exam or candidate not found")

    assignment = (
        db.query(models.ExamCandidate)
        .filter(and_(models.ExamCandidate.exam_id == exam_id, models.ExamCandidate.candidate_id == candidate_id))
        .first()
    )
    if not assignment:
        raise ValueError("Candidate is not assigned to this exam")

    existing_attempt = (
        db.query(models.ExamAttempt)
        .filter(and_(models.ExamAttempt.exam_id == exam_id, models.ExamAttempt.candidate_id == candidate_id))
        .filter(models.ExamAttempt.status != "submitted")
        .first()
    )
    if existing_attempt:
        return existing_attempt

    attempt = models.ExamAttempt(
        exam_id=exam_id,
        candidate_id=candidate_id,
        started_at=datetime.utcnow(),
        status="in_progress",
        total_marks=exam.total_marks,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempt(db: Session, attempt_id: int) -> models.ExamAttempt | None:
    return db.query(models.ExamAttempt).filter(models.ExamAttempt.id == attempt_id).first()


def save_answer(db: Session, attempt_id: int, question_id: int, selected_option: str) -> models.AttemptAnswer:
    attempt = get_attempt(db, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    question = get_question(db, question_id)
    if not question:
        raise ValueError("Question not found")

    existing = (
        db.query(models.AttemptAnswer)
        .filter(and_(models.AttemptAnswer.exam_attempt_id == attempt_id, models.AttemptAnswer.question_id == question_id))
        .first()
    )

    if existing:
        existing.selected_option = selected_option
        existing.is_correct = selected_option == question.correct_option
    else:
        existing = models.AttemptAnswer(
            exam_attempt_id=attempt_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=selected_option == question.correct_option,
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return existing


def submit_exam(db: Session, attempt_id: int) -> models.ExamAttempt:
    attempt = get_attempt(db, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    attempt.status = "submitted"
    attempt.submitted_at = datetime.utcnow()
    attempt.score = sum(answer.is_correct * answer.question.marks for answer in attempt.answers)
    db.commit()
    db.refresh(attempt)
    return attempt


def calculate_result(db: Session, attempt_id: int) -> models.Result:
    attempt = get_attempt(db, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")

    total_marks = attempt.total_marks or attempt.exam.total_marks
    score = sum(answer.is_correct * answer.question.marks for answer in attempt.answers)
    percentage = int((score / total_marks) * 100) if total_marks else 0
    passed = percentage >= 50

    existing_result = db.query(models.Result).filter(models.Result.exam_attempt_id == attempt_id).first()
    if existing_result:
        existing_result.score = score
        existing_result.total_marks = total_marks
        existing_result.percentage = percentage
        existing_result.passed = passed
        db.commit()
        db.refresh(existing_result)
        return existing_result

    result = models.Result(
        exam_id=attempt.exam_id,
        candidate_id=attempt.candidate_id,
        exam_attempt_id=attempt_id,
        score=score,
        total_marks=total_marks,
        percentage=percentage,
        passed=passed,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_result(db: Session, result_id: int) -> models.Result | None:
    return db.query(models.Result).filter(models.Result.id == result_id).first()


def get_result_by_attempt(db: Session, attempt_id: int) -> models.Result | None:
    return db.query(models.Result).filter(models.Result.exam_attempt_id == attempt_id).first()
