"""
User model for authentication and authorization.
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    STUDENT = "student"


class User(Base):
    """
    User model representing both admin and student users.
    
    Attributes:
        id: Primary key
        username: Unique username for login
        email: User email address
        password_hash: Hashed password
        full_name: User's full name
        role: Either 'admin' or 'student'
        created_at: Account creation timestamp
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole, native_enum=False), default=UserRole.STUDENT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exams_created = relationship("Exam", back_populates="creator")
    exam_attempts = relationship("ExamAttempt", back_populates="student")

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"
