"""
Pydantic schemas for exam results.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AttemptBase(BaseModel):
    """Base attempt schema."""
    exam_id: int


class AttemptCreate(AttemptBase):
    """Schema for starting an exam attempt."""
    pass


class AnswerDetail(BaseModel):
    """Detail of each answer in results."""
    question_id: int
    question_text: str
    selected_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    points: int

    class Config:
        from_attributes = True


class AttemptResult(BaseModel):
    """Exam result for student."""
    id: int
    exam_id: int
    exam_title: str
    started_at: datetime
    finished_at: Optional[datetime]
    score: Optional[float]
    total_questions: int
    correct_count: int
    is_completed: bool

    class Config:
        from_attributes = True


class AttemptResultDetail(AttemptResult):
    """Detailed exam result with answer breakdown."""
    answers: List[AnswerDetail] = []


class ActiveAttempt(BaseModel):
    """Schema for active/in-progress exam."""
    attempt_id: int
    exam_id: int
    exam_title: str
    started_at: datetime
    time_remaining_seconds: int
    current_question_index: int = 0
    total_questions: int
