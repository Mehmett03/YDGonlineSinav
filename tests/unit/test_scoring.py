"""
Unit tests for scoring service.
Tests the core scoring logic independently from the database.
"""
import pytest
from unittest.mock import MagicMock
from app.services.scoring_service import (
    calculate_score,
    is_answer_correct,
    validate_answer_option,
    get_grade_letter
)


class TestCalculateScore:
    """Test cases for calculate_score function."""

    def test_all_correct_answers(self):
        """Test scoring when all answers are correct."""
        # Mock questions
        questions = [
            MagicMock(id=1, correct_answer=MagicMock(value="A"), points=1),
            MagicMock(id=2, correct_answer=MagicMock(value="B"), points=1),
            MagicMock(id=3, correct_answer=MagicMock(value="C"), points=1),
        ]
        
        # Mock answers
        answers = [
            MagicMock(question_id=1, selected_answer="A"),
            MagicMock(question_id=2, selected_answer="B"),
            MagicMock(question_id=3, selected_answer="C"),
        ]
        
        score, correct, total = calculate_score(answers, questions)
        
        assert score == 100.0
        assert correct == 3
        assert total == 3

    def test_all_wrong_answers(self):
        """Test scoring when all answers are wrong."""
        questions = [
            MagicMock(id=1, correct_answer=MagicMock(value="A"), points=1),
            MagicMock(id=2, correct_answer=MagicMock(value="B"), points=1),
        ]
        
        answers = [
            MagicMock(question_id=1, selected_answer="B"),
            MagicMock(question_id=2, selected_answer="A"),
        ]
        
        score, correct, total = calculate_score(answers, questions)
        
        assert score == 0.0
        assert correct == 0
        assert total == 2

    def test_partial_correct_answers(self):
        """Test scoring with mixed correct and wrong answers."""
        questions = [
            MagicMock(id=1, correct_answer=MagicMock(value="A"), points=1),
            MagicMock(id=2, correct_answer=MagicMock(value="B"), points=1),
            MagicMock(id=3, correct_answer=MagicMock(value="C"), points=1),
            MagicMock(id=4, correct_answer=MagicMock(value="D"), points=1),
        ]
        
        answers = [
            MagicMock(question_id=1, selected_answer="A"),  # Correct
            MagicMock(question_id=2, selected_answer="A"),  # Wrong
            MagicMock(question_id=3, selected_answer="C"),  # Correct
            MagicMock(question_id=4, selected_answer="A"),  # Wrong
        ]
        
        score, correct, total = calculate_score(answers, questions)
        
        assert score == 50.0
        assert correct == 2
        assert total == 4

    def test_empty_questions(self):
        """Test scoring with no questions."""
        score, correct, total = calculate_score([], [])
        
        assert score == 0.0
        assert correct == 0
        assert total == 0

    def test_case_insensitive_answers(self):
        """Test that answer comparison is case-insensitive."""
        questions = [
            MagicMock(id=1, correct_answer=MagicMock(value="A"), points=1),
        ]
        
        answers = [
            MagicMock(question_id=1, selected_answer="a"),  # lowercase
        ]
        
        score, correct, total = calculate_score(answers, questions)
        
        assert score == 100.0
        assert correct == 1

    def test_weighted_scoring(self):
        """Test scoring with different point values."""
        questions = [
            MagicMock(id=1, correct_answer=MagicMock(value="A"), points=2),
            MagicMock(id=2, correct_answer=MagicMock(value="B"), points=3),
        ]
        
        # Only first question correct (2 points out of 5)
        answers = [
            MagicMock(question_id=1, selected_answer="A"),
            MagicMock(question_id=2, selected_answer="A"),
        ]
        
        score, correct, total = calculate_score(answers, questions)
        
        assert score == 40.0  # 2/5 * 100
        assert correct == 1


class TestIsAnswerCorrect:
    """Test cases for is_answer_correct function."""

    def test_correct_answer_uppercase(self):
        """Test correct answer with uppercase."""
        assert is_answer_correct("A", "A") is True

    def test_correct_answer_lowercase(self):
        """Test correct answer with lowercase."""
        assert is_answer_correct("a", "A") is True

    def test_wrong_answer(self):
        """Test wrong answer."""
        assert is_answer_correct("B", "A") is False

    def test_empty_answer(self):
        """Test empty answer."""
        assert is_answer_correct("", "A") is False
        assert is_answer_correct(None, "A") is False


class TestValidateAnswerOption:
    """Test cases for validate_answer_option function."""

    def test_valid_options(self):
        """Test all valid options."""
        assert validate_answer_option("A") is True
        assert validate_answer_option("B") is True
        assert validate_answer_option("C") is True
        assert validate_answer_option("D") is True

    def test_valid_options_lowercase(self):
        """Test lowercase valid options."""
        assert validate_answer_option("a") is True
        assert validate_answer_option("b") is True

    def test_invalid_options(self):
        """Test invalid options."""
        assert validate_answer_option("E") is False
        assert validate_answer_option("1") is False
        assert validate_answer_option("") is False
        assert validate_answer_option(None) is False


class TestGetGradeLetter:
    """Test cases for get_grade_letter function."""

    def test_grade_aa(self):
        """Test AA grade (90-100)."""
        assert get_grade_letter(100) == "AA"
        assert get_grade_letter(95) == "AA"
        assert get_grade_letter(90) == "AA"

    def test_grade_ba(self):
        """Test BA grade (85-89)."""
        assert get_grade_letter(89) == "BA"
        assert get_grade_letter(85) == "BA"

    def test_grade_bb(self):
        """Test BB grade (80-84)."""
        assert get_grade_letter(84) == "BB"
        assert get_grade_letter(80) == "BB"

    def test_grade_cb(self):
        """Test CB grade (75-79)."""
        assert get_grade_letter(79) == "CB"
        assert get_grade_letter(75) == "CB"

    def test_grade_cc(self):
        """Test CC grade (70-74)."""
        assert get_grade_letter(74) == "CC"
        assert get_grade_letter(70) == "CC"

    def test_grade_dc(self):
        """Test DC grade (65-69)."""
        assert get_grade_letter(69) == "DC"
        assert get_grade_letter(65) == "DC"

    def test_grade_dd(self):
        """Test DD grade (60-64)."""
        assert get_grade_letter(64) == "DD"
        assert get_grade_letter(60) == "DD"

    def test_grade_ff(self):
        """Test FF grade (0-59)."""
        assert get_grade_letter(59) == "FF"
        assert get_grade_letter(0) == "FF"
        assert get_grade_letter(45) == "FF"
