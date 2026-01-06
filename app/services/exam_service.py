"""
Exam and question management service.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.exam import Exam
from app.models.question import Question
from app.models.result import ExamAttempt
from app.schemas.exam import ExamCreate, QuestionCreate


def create_exam(db: Session, exam_data: ExamCreate, creator_id: int) -> Exam:
    """Create a new exam."""
    exam = Exam(
        title=exam_data.title,
        description=exam_data.description,
        duration_minutes=exam_data.duration_minutes,
        created_by=creator_id,
        is_active=True
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


def get_exam(db: Session, exam_id: int) -> Optional[Exam]:
    """Get an exam by ID."""
    return db.query(Exam).filter(Exam.id == exam_id).first()


def get_all_exams(db: Session, only_active: bool = False) -> List[Exam]:
    """Get all exams, optionally filtered by active status."""
    query = db.query(Exam)
    if only_active:
        query = query.filter(Exam.is_active == True)
    return query.order_by(Exam.created_at.desc()).all()


def get_exams_by_creator(db: Session, creator_id: int) -> List[Exam]:
    """Get all exams created by a specific admin."""
    return db.query(Exam).filter(Exam.created_by == creator_id).all()


def update_exam(db: Session, exam_id: int, exam_data: ExamCreate) -> Optional[Exam]:
    """Update an existing exam."""
    exam = get_exam(db, exam_id)
    if not exam:
        return None
    
    exam.title = exam_data.title
    exam.description = exam_data.description
    exam.duration_minutes = exam_data.duration_minutes
    db.commit()
    db.refresh(exam)
    return exam


def toggle_exam_active(db: Session, exam_id: int) -> Optional[Exam]:
    """Toggle exam active status."""
    exam = get_exam(db, exam_id)
    if not exam:
        return None
    exam.is_active = not exam.is_active
    db.commit()
    db.refresh(exam)
    return exam


def delete_exam(db: Session, exam_id: int) -> bool:
    """Delete an exam and its questions."""
    exam = get_exam(db, exam_id)
    if not exam:
        return False
    db.delete(exam)
    db.commit()
    return True


# Question Operations
def add_question(db: Session, exam_id: int, question_data: QuestionCreate) -> Optional[Question]:
    """Add a question to an exam."""
    exam = get_exam(db, exam_id)
    if not exam:
        return None
    
    question = Question(
        exam_id=exam_id,
        question_text=question_data.question_text,
        option_a=question_data.option_a,
        option_b=question_data.option_b,
        option_c=question_data.option_c,
        option_d=question_data.option_d,
        correct_answer=question_data.correct_answer,
        points=question_data.points
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_questions_for_exam(db: Session, exam_id: int) -> List[Question]:
    """Get all questions for an exam."""
    return db.query(Question).filter(Question.exam_id == exam_id).all()


def get_question(db: Session, question_id: int) -> Optional[Question]:
    """Get a question by ID."""
    return db.query(Question).filter(Question.id == question_id).first()


def update_question(db: Session, question_id: int, question_data: QuestionCreate) -> Optional[Question]:
    """Update a question."""
    question = get_question(db, question_id)
    if not question:
        return None
    
    question.question_text = question_data.question_text
    question.option_a = question_data.option_a
    question.option_b = question_data.option_b
    question.option_c = question_data.option_c
    question.option_d = question_data.option_d
    question.correct_answer = question_data.correct_answer
    question.points = question_data.points
    db.commit()
    db.refresh(question)
    return question


def delete_question(db: Session, question_id: int) -> bool:
    """Delete a question."""
    question = get_question(db, question_id)
    if not question:
        return False
    db.delete(question)
    db.commit()
    return True


def has_student_taken_exam(db: Session, user_id: int, exam_id: int) -> bool:
    """Check if a student has already completed this exam."""
    attempt = db.query(ExamAttempt).filter(
        ExamAttempt.user_id == user_id,
        ExamAttempt.exam_id == exam_id,
        ExamAttempt.is_completed == 1
    ).first()
    return attempt is not None


def get_active_attempt(db: Session, user_id: int, exam_id: int) -> Optional[ExamAttempt]:
    """Get an active (in-progress) exam attempt."""
    return db.query(ExamAttempt).filter(
        ExamAttempt.user_id == user_id,
        ExamAttempt.exam_id == exam_id,
        ExamAttempt.is_completed == 0
    ).first()
