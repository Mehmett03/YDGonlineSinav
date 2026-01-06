"""
Integration tests for exam flow.
Tests the complete exam workflow from creation to completion.
"""
import pytest
from datetime import datetime


class TestExamCreationFlow:
    """Test complete exam creation flow."""

    def test_create_exam_with_questions(self, db, admin_user):
        """Test creating an exam and adding questions."""
        from app.services import exam_service
        from app.schemas.exam import ExamCreate, QuestionCreate, AnswerOption
        
        # Create exam
        exam_data = ExamCreate(
            title="Integration Test Exam",
            description="Test exam for integration testing",
            duration_minutes=45
        )
        exam = exam_service.create_exam(db, exam_data, admin_user.id)
        
        assert exam.id is not None
        assert exam.title == "Integration Test Exam"
        assert exam.duration_minutes == 45
        
        # Add questions
        question_data = QuestionCreate(
            question_text="What is 2 + 2?",
            option_a="3",
            option_b="4",
            option_c="5",
            option_d="6",
            correct_answer=AnswerOption.B
        )
        question = exam_service.add_question(db, exam.id, question_data)
        
        assert question.id is not None
        assert question.exam_id == exam.id
        
        # Verify questions are linked
        questions = exam_service.get_questions_for_exam(db, exam.id)
        assert len(questions) == 1

    def test_exam_retrieval(self, db, sample_exam):
        """Test retrieving exam and its questions."""
        from app.services import exam_service
        
        # Get exam
        exam = exam_service.get_exam(db, sample_exam.id)
        assert exam is not None
        assert exam.title == "Test Sınavı"
        
        # Get questions
        questions = exam_service.get_questions_for_exam(db, sample_exam.id)
        assert len(questions) == 3


class TestExamAttemptFlow:
    """Test complete exam attempt flow."""

    def test_student_takes_exam(self, db, sample_exam, student_user):
        """Test a student taking an exam from start to finish."""
        from app.services import exam_service
        from app.services.scoring_service import calculate_score
        from app.models.result import ExamAttempt, UserAnswer
        
        # Verify student hasn't taken exam
        assert not exam_service.has_student_taken_exam(db, student_user.id, sample_exam.id)
        
        # Start exam attempt
        attempt = ExamAttempt(
            user_id=student_user.id,
            exam_id=sample_exam.id,
            started_at=datetime.utcnow()
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        
        assert attempt.id is not None
        assert attempt.is_completed == 0
        
        # Get questions
        questions = exam_service.get_questions_for_exam(db, sample_exam.id)
        
        # Submit answers (all correct)
        for q in questions:
            answer = UserAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_answer=q.correct_answer.value
            )
            db.add(answer)
        db.commit()
        
        # Calculate and save score
        answers = db.query(UserAnswer).filter(
            UserAnswer.attempt_id == attempt.id
        ).all()
        
        score, correct, total = calculate_score(answers, questions)
        
        # Complete attempt
        attempt.score = score
        attempt.is_completed = 1
        attempt.finished_at = datetime.utcnow()
        db.commit()
        
        assert attempt.score == 100.0
        assert exam_service.has_student_taken_exam(db, student_user.id, sample_exam.id)

    def test_duplicate_exam_prevention(self, db, sample_exam, student_user):
        """Test that a student cannot take the same exam twice."""
        from app.services import exam_service
        from app.models.result import ExamAttempt
        
        # First attempt - completed
        attempt1 = ExamAttempt(
            user_id=student_user.id,
            exam_id=sample_exam.id,
            started_at=datetime.utcnow(),
            finished_at=datetime.utcnow(),
            score=80.0,
            is_completed=1
        )
        db.add(attempt1)
        db.commit()
        
        # Verify student has taken exam
        assert exam_service.has_student_taken_exam(db, student_user.id, sample_exam.id) is True
        
        # Active attempt should return None (no new attempt allowed after completion)
        active = exam_service.get_active_attempt(db, student_user.id, sample_exam.id)
        assert active is None


class TestExamScoring:
    """Test exam scoring integration."""

    def test_partial_score_calculation(self, db, sample_exam, student_user):
        """Test partial scoring when some answers are wrong."""
        from app.services import exam_service
        from app.services.scoring_service import calculate_score
        from app.models.result import ExamAttempt, UserAnswer
        
        # Start attempt
        attempt = ExamAttempt(
            user_id=student_user.id,
            exam_id=sample_exam.id,
            started_at=datetime.utcnow()
        )
        db.add(attempt)
        db.commit()
        
        questions = exam_service.get_questions_for_exam(db, sample_exam.id)
        
        # Submit mixed answers (1 correct, 2 wrong)
        for i, q in enumerate(questions):
            if i == 0:
                answer_value = q.correct_answer.value  # Correct
            else:
                # Wrong answer - pick different option
                wrong_options = [o for o in ['A', 'B', 'C', 'D'] if o != q.correct_answer.value]
                answer_value = wrong_options[0]
            
            answer = UserAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_answer=answer_value
            )
            db.add(answer)
        db.commit()
        
        answers = db.query(UserAnswer).filter(
            UserAnswer.attempt_id == attempt.id
        ).all()
        
        score, correct, total = calculate_score(answers, questions)
        
        # 1 out of 3 correct = 33.33%
        assert 33.0 <= score <= 34.0
        assert correct == 1
        assert total == 3
