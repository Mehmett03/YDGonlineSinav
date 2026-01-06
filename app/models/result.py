"""
Result models for exam attempts and answers.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ExamAttempt(Base):
    """
    ExamAttempt model tracking a student's exam session.
    
    Attributes:
        id: Primary key
        user_id: Student who took the exam
        exam_id: The exam taken
        started_at: When the attempt began
        finished_at: When the attempt ended (auto or manual)
        score: Final calculated score (0-100)
        is_completed: Whether the exam was finished
    """
    __tablename__ = "exam_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    score = Column(Float, nullable=True)
    is_completed = Column(Integer, default=0)  # 0=in progress, 1=completed

    # Relationships
    student = relationship("User", back_populates="exam_attempts")
    exam = relationship("Exam", back_populates="attempts")
    answers = relationship("UserAnswer", back_populates="attempt", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ExamAttempt(user_id={self.user_id}, exam_id={self.exam_id}, score={self.score})>"

    @property
    def is_expired(self) -> bool:
        """Check if the exam time has expired."""
        if self.finished_at:
            return True
        if not self.exam:
            return False
        elapsed = (datetime.utcnow() - self.started_at).total_seconds() / 60
        return elapsed >= self.exam.duration_minutes


class UserAnswer(Base):
    """
    UserAnswer model storing individual question answers.
    
    Attributes:
        id: Primary key
        attempt_id: The exam attempt this answer belongs to
        question_id: The question being answered
        selected_answer: The option selected (A, B, C, or D)
    """
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_answer = Column(String(1), nullable=True)  # A, B, C, D or None

    # Relationships
    attempt = relationship("ExamAttempt", back_populates="answers")
    question = relationship("Question", back_populates="user_answers")

    def __repr__(self):
        return f"<UserAnswer(question_id={self.question_id}, answer='{self.selected_answer}')>"

    @property
    def is_correct(self) -> bool:
        """Check if this answer is correct."""
        if not self.selected_answer or not self.question:
            return False
        return self.question.correct_answer.value == self.selected_answer.upper()
