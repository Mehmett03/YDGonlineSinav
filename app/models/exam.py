"""
Exam model for managing exams.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Exam(Base):
    """
    Exam model representing a test/quiz.
    
    Attributes:
        id: Primary key
        title: Exam title
        description: Exam description
        duration_minutes: Time limit in minutes
        is_active: Whether the exam is currently available
        created_by: Admin user who created the exam
        created_at: Exam creation timestamp
    """
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=30)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="exams_created")
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")
    attempts = relationship("ExamAttempt", back_populates="exam")

    def __repr__(self):
        return f"<Exam(title='{self.title}', duration={self.duration_minutes}min)>"

    @property
    def question_count(self) -> int:
        """Return the number of questions in this exam."""
        return len(self.questions) if self.questions else 0
