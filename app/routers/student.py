"""
Student router for taking exams and viewing results.
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.exam import Exam
from app.models.result import ExamAttempt, UserAnswer
from app.schemas.exam import ExamStudentView, AnswerSubmission
from app.schemas.result import AttemptResult, AttemptResultDetail, ActiveAttempt
from app.services.auth_service import get_current_student
from app.services import exam_service
from app.services.scoring_service import calculate_score, calculate_time_remaining, is_exam_expired

router = APIRouter(prefix="/student", tags=["Student"])
templates = Jinja2Templates(directory="app/templates")


def get_student_from_cookie(request: Request, db: Session = Depends(get_db)) -> User:
    """Get student user from cookie token."""
    from app.services.auth_service import decode_access_token
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user or user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Student access required")
    
    return user


# ==================== API Endpoints ====================

@router.get("/exams", response_model=List[ExamStudentView])
def get_available_exams(
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student)
):
    """Get all available exams for student."""
    exams = exam_service.get_all_exams(db, only_active=True)
    result = []
    for exam in exams:
        is_taken = exam_service.has_student_taken_exam(db, current_student.id, exam.id)
        result.append(ExamStudentView(
            id=exam.id,
            title=exam.title,
            description=exam.description,
            duration_minutes=exam.duration_minutes,
            question_count=len(exam.questions),
            is_taken=is_taken
        ))
    return result


@router.post("/exams/{exam_id}/start")
def start_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student)
):
    """Start an exam attempt."""
    exam = exam_service.get_exam(db, exam_id)
    if not exam or not exam.is_active:
        raise HTTPException(status_code=404, detail="Sınav bulunamadı veya aktif değil")
    
    # Check if already taken
    if exam_service.has_student_taken_exam(db, current_student.id, exam_id):
        raise HTTPException(
            status_code=400, 
            detail="Bu sınava zaten girdiniz. Aynı sınava ikinci kez girilemez."
        )
    
    # Check for existing active attempt
    active_attempt = exam_service.get_active_attempt(db, current_student.id, exam_id)
    if active_attempt:
        # Check if expired
        if is_exam_expired(active_attempt.started_at, exam.duration_minutes):
            # Auto-complete expired attempt
            complete_attempt(db, active_attempt)
            raise HTTPException(
                status_code=400,
                detail="Önceki sınav süreniz doldu ve otomatik olarak tamamlandı."
            )
        return {"attempt_id": active_attempt.id, "message": "Devam eden sınav bulundu"}
    
    # Create new attempt
    attempt = ExamAttempt(
        user_id=current_student.id,
        exam_id=exam_id,
        started_at=datetime.utcnow()
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return {"attempt_id": attempt.id, "message": "Sınav başlatıldı"}


@router.post("/attempts/{attempt_id}/answer")
def submit_answer(
    attempt_id: int,
    answer: AnswerSubmission,
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student)
):
    """Submit or update an answer for a question."""
    attempt = db.query(ExamAttempt).filter(
        ExamAttempt.id == attempt_id,
        ExamAttempt.user_id == current_student.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Sınav denemesi bulunamadı")
    
    if attempt.is_completed:
        raise HTTPException(status_code=400, detail="Bu sınav zaten tamamlanmış")
    
    # Check if time expired
    exam = exam_service.get_exam(db, attempt.exam_id)
    if is_exam_expired(attempt.started_at, exam.duration_minutes):
        complete_attempt(db, attempt)
        raise HTTPException(status_code=400, detail="Sınav süresi doldu")
    
    # Update or create answer
    existing_answer = db.query(UserAnswer).filter(
        UserAnswer.attempt_id == attempt_id,
        UserAnswer.question_id == answer.question_id
    ).first()
    
    if existing_answer:
        existing_answer.selected_answer = answer.selected_answer.value if answer.selected_answer else None
    else:
        new_answer = UserAnswer(
            attempt_id=attempt_id,
            question_id=answer.question_id,
            selected_answer=answer.selected_answer.value if answer.selected_answer else None
        )
        db.add(new_answer)
    
    db.commit()
    return {"message": "Cevap kaydedildi"}


@router.post("/attempts/{attempt_id}/submit")
def submit_exam(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student)
):
    """Submit and complete an exam."""
    attempt = db.query(ExamAttempt).filter(
        ExamAttempt.id == attempt_id,
        ExamAttempt.user_id == current_student.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Sınav denemesi bulunamadı")
    
    if attempt.is_completed:
        raise HTTPException(status_code=400, detail="Bu sınav zaten tamamlanmış")
    
    complete_attempt(db, attempt)
    return {"message": "Sınav tamamlandı", "score": attempt.score}


@router.get("/results", response_model=List[AttemptResult])
def get_my_results(
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student)
):
    """Get all exam results for current student."""
    attempts = db.query(ExamAttempt).filter(
        ExamAttempt.user_id == current_student.id,
        ExamAttempt.is_completed == 1
    ).all()
    
    results = []
    for attempt in attempts:
        exam = exam_service.get_exam(db, attempt.exam_id)
        answers = db.query(UserAnswer).filter(UserAnswer.attempt_id == attempt.id).all()
        correct_count = sum(1 for a in answers if a.is_correct)
        
        results.append(AttemptResult(
            id=attempt.id,
            exam_id=attempt.exam_id,
            exam_title=exam.title if exam else "Sınav Silindi",
            started_at=attempt.started_at,
            finished_at=attempt.finished_at,
            score=attempt.score,
            total_questions=len(exam.questions) if exam else 0,
            correct_count=correct_count,
            is_completed=attempt.is_completed == 1
        ))
    
    return results


def complete_attempt(db: Session, attempt: ExamAttempt):
    """Complete an exam attempt and calculate score."""
    exam = exam_service.get_exam(db, attempt.exam_id)
    if not exam:
        return
    
    # Get all answers
    answers = db.query(UserAnswer).filter(UserAnswer.attempt_id == attempt.id).all()
    questions = exam_service.get_questions_for_exam(db, attempt.exam_id)
    
    # Calculate score
    score, correct_count, total = calculate_score(answers, questions)
    
    # Update attempt
    attempt.finished_at = datetime.utcnow()
    attempt.score = score
    attempt.is_completed = 1
    db.commit()


# ==================== Web Page Endpoints ====================

@router.get("/dashboard", response_class=HTMLResponse)
def student_dashboard(request: Request, db: Session = Depends(get_db)):
    """Student dashboard page."""
    try:
        student = get_student_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    exams = exam_service.get_all_exams(db, only_active=True)
    exam_list = []
    for exam in exams:
        is_taken = exam_service.has_student_taken_exam(db, student.id, exam.id)
        exam_list.append({
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "duration_minutes": exam.duration_minutes,
            "question_count": len(exam.questions),
            "is_taken": is_taken
        })
    
    return templates.TemplateResponse(
        "student/dashboard.html",
        {"request": request, "user": student, "exams": exam_list}
    )


@router.get("/exam/{exam_id}/take", response_class=HTMLResponse)
def take_exam_page(request: Request, exam_id: int, db: Session = Depends(get_db)):
    """Exam taking page."""
    try:
        student = get_student_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    exam = exam_service.get_exam(db, exam_id)
    if not exam or not exam.is_active:
        raise HTTPException(status_code=404, detail="Sınav bulunamadı")
    
    # Check if already taken
    if exam_service.has_student_taken_exam(db, student.id, exam_id):
        return templates.TemplateResponse(
            "student/error.html",
            {"request": request, "user": student, 
             "error": "Bu sınava zaten girdiniz. Aynı sınava ikinci kez girilemez."}
        )
    
    # Get or create attempt
    attempt = exam_service.get_active_attempt(db, student.id, exam_id)
    if not attempt:
        attempt = ExamAttempt(
            user_id=student.id,
            exam_id=exam_id,
            started_at=datetime.utcnow()
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    
    # Check if expired
    if is_exam_expired(attempt.started_at, exam.duration_minutes):
        complete_attempt(db, attempt)
        return RedirectResponse(url=f"/student/result/{attempt.id}", status_code=303)
    
    # Get questions
    questions = exam_service.get_questions_for_exam(db, exam_id)
    time_remaining = calculate_time_remaining(attempt.started_at, exam.duration_minutes)
    
    # Get existing answers
    existing_answers = db.query(UserAnswer).filter(
        UserAnswer.attempt_id == attempt.id
    ).all()
    answers_map = {a.question_id: a.selected_answer for a in existing_answers}
    
    return templates.TemplateResponse(
        "student/exam_take.html",
        {
            "request": request,
            "user": student,
            "exam": exam,
            "questions": questions,
            "attempt_id": attempt.id,
            "time_remaining": time_remaining,
            "answers_map": answers_map
        }
    )


@router.post("/exam/{exam_id}/submit-form")
def submit_exam_form(
    request: Request,
    exam_id: int,
    db: Session = Depends(get_db)
):
    """Process exam submission from form."""
    try:
        student = get_student_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    attempt = exam_service.get_active_attempt(db, student.id, exam_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Aktif sınav bulunamadı")
    
    complete_attempt(db, attempt)
    return RedirectResponse(url=f"/student/result/{attempt.id}", status_code=303)


@router.post("/answer-form")
async def save_answer_form(
    request: Request,
    db: Session = Depends(get_db)
):
    """Save answer via AJAX form."""
    try:
        student = get_student_from_cookie(request, db)
    except HTTPException:
        return {"error": "Not authenticated"}
    
    form_data = await request.form()
    attempt_id = int(form_data.get("attempt_id"))
    question_id = int(form_data.get("question_id"))
    selected_answer = form_data.get("selected_answer")
    
    # Validate attempt belongs to student
    attempt = db.query(ExamAttempt).filter(
        ExamAttempt.id == attempt_id,
        ExamAttempt.user_id == student.id
    ).first()
    
    if not attempt or attempt.is_completed:
        return {"error": "Invalid attempt"}
    
    # Update or create answer
    existing = db.query(UserAnswer).filter(
        UserAnswer.attempt_id == attempt_id,
        UserAnswer.question_id == question_id
    ).first()
    
    if existing:
        existing.selected_answer = selected_answer
    else:
        db.add(UserAnswer(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_answer=selected_answer
        ))
    
    db.commit()
    return {"success": True}


@router.get("/result/{attempt_id}", response_class=HTMLResponse)
def result_page(request: Request, attempt_id: int, db: Session = Depends(get_db)):
    """Exam result page."""
    try:
        student = get_student_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    attempt = db.query(ExamAttempt).filter(
        ExamAttempt.id == attempt_id,
        ExamAttempt.user_id == student.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Sonuç bulunamadı")
    
    exam = exam_service.get_exam(db, attempt.exam_id)
    questions = exam_service.get_questions_for_exam(db, attempt.exam_id)
    answers = db.query(UserAnswer).filter(UserAnswer.attempt_id == attempt_id).all()
    answers_map = {a.question_id: a for a in answers}
    
    # Build detailed results
    answer_details = []
    correct_count = 0
    for q in questions:
        user_answer = answers_map.get(q.id)
        is_correct = user_answer and user_answer.selected_answer == q.correct_answer.value
        if is_correct:
            correct_count += 1
        answer_details.append({
            "question": q,
            "selected": user_answer.selected_answer if user_answer else None,
            "is_correct": is_correct
        })
    
    from app.services.scoring_service import get_grade_letter
    grade = get_grade_letter(attempt.score) if attempt.score else "FF"
    
    return templates.TemplateResponse(
        "student/result.html",
        {
            "request": request,
            "user": student,
            "exam": exam,
            "attempt": attempt,
            "answer_details": answer_details,
            "correct_count": correct_count,
            "total_questions": len(questions),
            "grade": grade
        }
    )


@router.get("/results-page", response_class=HTMLResponse)
def results_list_page(request: Request, db: Session = Depends(get_db)):
    """All results page."""
    try:
        student = get_student_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    attempts = db.query(ExamAttempt).filter(
        ExamAttempt.user_id == student.id,
        ExamAttempt.is_completed == 1
    ).order_by(ExamAttempt.finished_at.desc()).all()
    
    results = []
    for attempt in attempts:
        exam = exam_service.get_exam(db, attempt.exam_id)
        results.append({
            "attempt": attempt,
            "exam_title": exam.title if exam else "Sınav Silindi"
        })
    
    return templates.TemplateResponse(
        "student/results.html",
        {"request": request, "user": student, "results": results}
    )
