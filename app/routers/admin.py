"""
Admin router for exam and question management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.exam import Exam
from app.schemas.exam import ExamCreate, ExamResponse, QuestionCreate, QuestionResponse, ExamWithQuestions
from app.services.auth_service import get_current_admin
from app.services import exam_service

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="app/templates")


def get_admin_from_cookie(request: Request, db: Session = Depends(get_db)) -> User:
    """Get admin user from cookie token."""
    from app.services.auth_service import decode_access_token
    from app.models.user import UserRole
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user


# ==================== API Endpoints ====================

@router.post("/exams", response_model=ExamResponse)
def create_exam(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Create a new exam."""
    exam = exam_service.create_exam(db, exam_data, current_admin.id)
    return exam


@router.get("/exams", response_model=List[ExamResponse])
def get_all_exams(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get all exams."""
    exams = exam_service.get_all_exams(db)
    return exams


@router.get("/exams/{exam_id}", response_model=ExamWithQuestions)
def get_exam_with_questions(
    exam_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get an exam with all its questions."""
    exam = exam_service.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Sınav bulunamadı")
    return exam


@router.put("/exams/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Update an exam."""
    exam = exam_service.update_exam(db, exam_id, exam_data)
    if not exam:
        raise HTTPException(status_code=404, detail="Sınav bulunamadı")
    return exam


@router.post("/exams/{exam_id}/toggle-active", response_model=ExamResponse)
def toggle_exam_active_status(
    exam_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Toggle exam active status."""
    exam = exam_service.toggle_exam_active(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Sınav bulunamadı")
    return exam


@router.delete("/exams/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Delete an exam."""
    if not exam_service.delete_exam(db, exam_id):
        raise HTTPException(status_code=404, detail="Sınav bulunamadı")
    return {"message": "Sınav silindi"}


@router.post("/exams/{exam_id}/questions", response_model=QuestionResponse)
def add_question(
    exam_id: int,
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Add a question to an exam."""
    question = exam_service.add_question(db, exam_id, question_data)
    if not question:
        raise HTTPException(status_code=404, detail="Sınav bulunamadı")
    return question


@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Update a question."""
    question = exam_service.update_question(db, question_id, question_data)
    if not question:
        raise HTTPException(status_code=404, detail="Soru bulunamadı")
    return question


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Delete a question."""
    if not exam_service.delete_question(db, question_id):
        raise HTTPException(status_code=404, detail="Soru bulunamadı")
    return {"message": "Soru silindi"}


# ==================== Web Page Endpoints ====================

@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """Admin dashboard page."""
    try:
        admin = get_admin_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    exams = exam_service.get_all_exams(db)
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "user": admin, "exams": exams}
    )


@router.get("/exam/create", response_class=HTMLResponse)
def create_exam_page(request: Request, db: Session = Depends(get_db)):
    """Exam creation page."""
    try:
        admin = get_admin_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    return templates.TemplateResponse(
        "admin/exam_create.html",
        {"request": request, "user": admin}
    )


@router.post("/exam/create-form")
def create_exam_form(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    duration_minutes: int = Form(...),
    db: Session = Depends(get_db)
):
    """Process exam creation form."""
    try:
        admin = get_admin_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    exam_data = ExamCreate(
        title=title,
        description=description,
        duration_minutes=duration_minutes
    )
    exam = exam_service.create_exam(db, exam_data, admin.id)
    
    return RedirectResponse(url=f"/admin/exam/{exam.id}/questions", status_code=303)


@router.get("/exam/{exam_id}/questions", response_class=HTMLResponse)
def exam_questions_page(
    request: Request,
    exam_id: int,
    db: Session = Depends(get_db)
):
    """Exam questions management page."""
    try:
        admin = get_admin_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    exam = exam_service.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Sınav bulunamadı")
    
    questions = exam_service.get_questions_for_exam(db, exam_id)
    
    return templates.TemplateResponse(
        "admin/question_add.html",
        {"request": request, "user": admin, "exam": exam, "questions": questions}
    )


@router.post("/exam/{exam_id}/question-form")
def add_question_form(
    request: Request,
    exam_id: int,
    question_text: str = Form(...),
    option_a: str = Form(...),
    option_b: str = Form(...),
    option_c: str = Form(...),
    option_d: str = Form(...),
    correct_answer: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process question addition form."""
    try:
        admin = get_admin_from_cookie(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login-page", status_code=303)
    
    from app.schemas.exam import AnswerOption
    question_data = QuestionCreate(
        question_text=question_text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_answer=AnswerOption(correct_answer)
    )
    exam_service.add_question(db, exam_id, question_data)
    
    return RedirectResponse(url=f"/admin/exam/{exam_id}/questions", status_code=303)
