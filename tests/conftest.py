"""
Pytest configuration and fixtures.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.services.auth_service import get_password_hash


# Test database URL (SQLite for simplicity in unit tests)
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    """Create a test admin user."""
    user = User(
        username="test_admin",
        email="admin@test.com",
        full_name="Test Admin",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def student_user(db):
    """Create a test student user."""
    user = User(
        username="test_student",
        email="student@test.com",
        full_name="Test Student",
        password_hash=get_password_hash("student123"),
        role=UserRole.STUDENT
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_exam(db, admin_user):
    """Create a sample exam with questions."""
    from app.models.exam import Exam
    from app.models.question import Question, AnswerOption
    
    exam = Exam(
        title="Test Sınavı",
        description="Test açıklaması",
        duration_minutes=30,
        created_by=admin_user.id,
        is_active=True
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    
    # Add questions
    questions = [
        Question(
            exam_id=exam.id,
            question_text="1 + 1 = ?",
            option_a="1",
            option_b="2",
            option_c="3",
            option_d="4",
            correct_answer=AnswerOption.B
        ),
        Question(
            exam_id=exam.id,
            question_text="Türkiye'nin başkenti neresidir?",
            option_a="İstanbul",
            option_b="Ankara",
            option_c="İzmir",
            option_d="Bursa",
            correct_answer=AnswerOption.B
        ),
        Question(
            exam_id=exam.id,
            question_text="Python hangi tür bir dildir?",
            option_a="Compiled",
            option_b="Assembly",
            option_c="Interpreted",
            option_d="Binary",
            correct_answer=AnswerOption.C
        )
    ]
    
    for q in questions:
        db.add(q)
    db.commit()
    
    return exam
