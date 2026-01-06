"""
Pydantic schemas for exam-related operations.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AnswerOption(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


# Question Schemas
class QuestionBase(BaseModel):
    """Base question schema."""
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: AnswerOption
    points: int = 1


class QuestionCreate(QuestionBase):
    """Schema for creating a question."""
    pass


class QuestionResponse(QuestionBase):
    """Schema for question response (admin view)."""
    id: int
    exam_id: int

    class Config:
        from_attributes = True


class QuestionStudentView(BaseModel):
    """Schema for student view (hides correct answer)."""
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    class Config:
        from_attributes = True


# Exam Schemas
class ExamBase(BaseModel):
    """Base exam schema."""
    title: str
    description: Optional[str] = None
    duration_minutes: int = 30


class ExamCreate(ExamBase):
    """Schema for creating an exam."""
    pass


class ExamResponse(ExamBase):
    """Schema for exam response."""
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    question_count: int = 0

    class Config:
        from_attributes = True


class ExamWithQuestions(ExamResponse):
    """Exam with all questions (admin view)."""
    questions: List[QuestionResponse] = []


class ExamStudentView(ExamBase):
    """Exam for student view (only active exams)."""
    id: int
    question_count: int = 0
    is_taken: bool = False

    class Config:
        from_attributes = True


# Answer Submission
class AnswerSubmission(BaseModel):
    """Schema for submitting an answer."""
    question_id: int
    selected_answer: Optional[AnswerOption] = None


class ExamSubmission(BaseModel):
    """Schema for submitting entire exam."""
    answers: List[AnswerSubmission]
