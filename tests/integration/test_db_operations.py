"""
Integration tests for database operations.
Tests CRUD operations with actual database.
"""
import pytest


class TestUserOperations:
    """Test user database operations."""

    def test_create_user(self, db):
        """Test creating a new user."""
        from app.services.auth_service import create_user
        from app.models.user import UserRole
        
        user = create_user(
            db=db,
            username="newuser",
            email="new@test.com",
            full_name="New User",
            password="password123",
            role=UserRole.STUDENT
        )
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "new@test.com"
        assert user.role == UserRole.STUDENT

    def test_authenticate_user(self, db):
        """Test user authentication."""
        from app.services.auth_service import create_user, authenticate_user
        from app.models.user import UserRole
        
        # Create user
        create_user(
            db=db,
            username="authtest",
            email="auth@test.com",
            full_name="Auth Test",
            password="correctpassword",
            role=UserRole.STUDENT
        )
        
        # Test correct password
        user = authenticate_user(db, "authtest", "correctpassword")
        assert user is not None
        assert user.username == "authtest"
        
        # Test wrong password
        user = authenticate_user(db, "authtest", "wrongpassword")
        assert user is None

    def test_duplicate_username_prevention(self, db):
        """Test that duplicate usernames are not allowed."""
        from app.services.auth_service import create_user
        from app.models.user import UserRole
        from sqlalchemy.exc import IntegrityError
        
        create_user(
            db=db,
            username="duplicate",
            email="unique1@test.com",
            full_name="First User",
            password="password",
            role=UserRole.STUDENT
        )
        
        with pytest.raises(IntegrityError):
            create_user(
                db=db,
                username="duplicate",
                email="unique2@test.com",
                full_name="Second User",
                password="password",
                role=UserRole.STUDENT
            )


class TestExamOperations:
    """Test exam database operations."""

    def test_exam_crud(self, db, admin_user):
        """Test complete CRUD operations on exams."""
        from app.services import exam_service
        from app.schemas.exam import ExamCreate
        
        # Create
        exam_data = ExamCreate(
            title="CRUD Test Exam",
            description="Testing CRUD",
            duration_minutes=60
        )
        exam = exam_service.create_exam(db, exam_data, admin_user.id)
        exam_id = exam.id
        
        assert exam.title == "CRUD Test Exam"
        
        # Read
        retrieved = exam_service.get_exam(db, exam_id)
        assert retrieved is not None
        assert retrieved.title == "CRUD Test Exam"
        
        # Update
        update_data = ExamCreate(
            title="Updated Exam",
            description="Updated description",
            duration_minutes=90
        )
        updated = exam_service.update_exam(db, exam_id, update_data)
        assert updated.title == "Updated Exam"
        assert updated.duration_minutes == 90
        
        # Delete
        result = exam_service.delete_exam(db, exam_id)
        assert result is True
        
        deleted = exam_service.get_exam(db, exam_id)
        assert deleted is None

    def test_exam_questions_cascade_delete(self, db, sample_exam):
        """Test that deleting an exam also deletes its questions."""
        from app.services import exam_service
        from app.models.question import Question
        
        exam_id = sample_exam.id
        
        # Verify questions exist
        questions = exam_service.get_questions_for_exam(db, exam_id)
        assert len(questions) > 0
        
        # Delete exam
        exam_service.delete_exam(db, exam_id)
        
        # Verify questions are deleted (cascade)
        remaining = db.query(Question).filter(Question.exam_id == exam_id).all()
        assert len(remaining) == 0


class TestQuestionOperations:
    """Test question database operations."""

    def test_add_multiple_questions(self, db, admin_user):
        """Test adding multiple questions to an exam."""
        from app.services import exam_service
        from app.schemas.exam import ExamCreate, QuestionCreate, AnswerOption
        
        # Create exam
        exam_data = ExamCreate(title="Multi Question Exam", duration_minutes=30)
        exam = exam_service.create_exam(db, exam_data, admin_user.id)
        
        # Add multiple questions
        for i in range(5):
            q_data = QuestionCreate(
                question_text=f"Question {i+1}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer=AnswerOption.A
            )
            exam_service.add_question(db, exam.id, q_data)
        
        # Verify all questions added
        questions = exam_service.get_questions_for_exam(db, exam.id)
        assert len(questions) == 5

    def test_update_question(self, db, sample_exam):
        """Test updating a question."""
        from app.services import exam_service
        from app.schemas.exam import QuestionCreate, AnswerOption
        
        questions = exam_service.get_questions_for_exam(db, sample_exam.id)
        question = questions[0]
        
        update_data = QuestionCreate(
            question_text="Updated question text",
            option_a="New A",
            option_b="New B",
            option_c="New C",
            option_d="New D",
            correct_answer=AnswerOption.D
        )
        
        updated = exam_service.update_question(db, question.id, update_data)
        
        assert updated.question_text == "Updated question text"
        assert updated.correct_answer == AnswerOption.D
