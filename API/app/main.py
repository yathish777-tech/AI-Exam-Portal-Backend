from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import Base, SessionLocal, engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Exam Management API", version="1.0.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/exams", response_model=schemas.ExamOut, status_code=status.HTTP_201_CREATED)
def create_exam(exam: schemas.ExamCreate, db: Session = Depends(get_db)):
    return crud.create_exam(db, exam)


@app.get("/exams", response_model=List[schemas.ExamOut])
def get_exams(db: Session = Depends(get_db)):
    return crud.get_exams(db)


@app.get("/exams/{exam_id}", response_model=schemas.ExamOut)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = crud.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@app.put("/exams/{exam_id}", response_model=schemas.ExamOut)
def update_exam(exam_id: int, exam: schemas.ExamUpdate, db: Session = Depends(get_db)):
    updated = crud.update_exam(db, exam_id, exam)
    if not updated:
        raise HTTPException(status_code=404, detail="Exam not found")
    return updated


@app.delete("/exams/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_exam(db, exam_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exam not found")
    return {"message": "Exam deleted successfully"}


@app.post("/exams/{exam_id}/publish", response_model=schemas.ExamOut)
def publish_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = crud.publish_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@app.post("/exams/{exam_id}/schedule", response_model=schemas.ExamOut)
def schedule_exam(exam_id: int, payload: schemas.ScheduleExamRequest, db: Session = Depends(get_db)):
    exam = crud.schedule_exam(db, exam_id, payload.scheduled_at)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@app.post("/exams/{exam_id}/questions", response_model=schemas.QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(exam_id: int, question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_question(db, exam_id, question)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/exams/{exam_id}/questions", response_model=List[schemas.QuestionOut])
def get_questions(exam_id: int, db: Session = Depends(get_db)):
    return crud.get_questions(db, exam_id)


@app.put("/questions/{question_id}", response_model=schemas.QuestionOut)
def update_question(question_id: int, question: schemas.QuestionUpdate, db: Session = Depends(get_db)):
    updated = crud.update_question(db, question_id, question)
    if not updated:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated


@app.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_question(db, question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}


@app.post("/candidates", response_model=schemas.CandidateOut, status_code=status.HTTP_201_CREATED)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db)):
    return crud.create_candidate(db, candidate)


@app.post("/exams/{exam_id}/candidates", response_model=schemas.CandidateOut)
def assign_candidate(exam_id: int, payload: schemas.AssignCandidateRequest, db: Session = Depends(get_db)):
    try:
        assignment = crud.assign_candidate(db, exam_id, payload.candidate_id)
        return assignment.candidate
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.delete("/exams/{exam_id}/candidates/{candidate_id}")
def remove_candidate(exam_id: int, candidate_id: int, db: Session = Depends(get_db)):
    removed = crud.remove_candidate(db, exam_id, candidate_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Candidate assignment not found")
    return {"message": "Candidate removed from exam"}


@app.get("/exams/{exam_id}/candidates", response_model=List[schemas.CandidateOut])
def get_assigned_candidates(exam_id: int, db: Session = Depends(get_db)):
    return crud.get_assigned_candidates(db, exam_id)


@app.post("/attempts/start", response_model=schemas.ExamAttemptOut)
def start_exam(payload: schemas.StartExamRequest, db: Session = Depends(get_db)):
    try:
        attempt = crud.start_exam(db, payload.exam_id, payload.candidate_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return attempt


@app.get("/attempts/{attempt_id}", response_model=schemas.ExamAttemptOut)
def get_attempt(attempt_id: int, db: Session = Depends(get_db)):
    attempt = crud.get_attempt(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt


@app.post("/attempts/{attempt_id}/answers", response_model=schemas.AttemptAnswerOut)
def save_answer(attempt_id: int, payload: schemas.SaveAnswerRequest, db: Session = Depends(get_db)):
    try:
        return crud.save_answer(db, attempt_id, payload.question_id, payload.selected_option)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/attempts/{attempt_id}/submit", response_model=schemas.ExamAttemptOut)
def submit_exam(attempt_id: int, db: Session = Depends(get_db)):
    try:
        return crud.submit_exam(db, attempt_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/results/calculate/{attempt_id}", response_model=schemas.ResultOut)
def calculate_result(attempt_id: int, db: Session = Depends(get_db)):
    try:
        return crud.calculate_result(db, attempt_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/results/{result_id}", response_model=schemas.ResultOut)
def get_result(result_id: int, db: Session = Depends(get_db)):
    result = crud.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@app.get("/attempts/{attempt_id}/result", response_model=schemas.ResultOut)
def get_attempt_result(attempt_id: int, db: Session = Depends(get_db)):
    result = crud.get_result_by_attempt(db, attempt_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result
