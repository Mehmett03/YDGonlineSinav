"""
Question model for exam questions.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class AnswerOption(str, enum.Enum):
    """Valid answer options."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Question(Base):
    """
    Question model representing individual exam questions.
    
    Attributes:
        id: Primary key
        exam_id: Foreign key to parent exam
        question_text: The question content
        option_a/b/c/d: Four answer options
        correct_answer: The correct option (A, B, C, or D)
        points: Points awarded for correct answer
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)
    correct_answer = Column(SQLEnum(AnswerOption, native_enum=False), nullable=False)
    points = Column(Integer, default=1)

    # Relationships
    exam = relationship("Exam", back_populates="questions")
    user_answers = relationship("UserAnswer", back_populates="question")

    def __repr__(self):
        return f"<Question(id={self.id}, exam_id={self.exam_id})>"

    def is_correct(self, answer: str) -> bool:
        """Check if the given answer is correct."""
        return self.correct_answer.value == answer.upper()
