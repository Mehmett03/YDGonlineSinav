"""
Unit tests for validation logic.
Tests question-answer validation independently.
"""
import pytest
from app.services.scoring_service import validate_answer_option


class TestQuestionValidation:
    """Test cases for question-related validation."""

    def test_valid_answer_options(self):
        """Test that valid answer options are accepted."""
        valid_options = ["A", "B", "C", "D", "a", "b", "c", "d"]
        for option in valid_options:
            assert validate_answer_option(option) is True, f"Option {option} should be valid"

    def test_invalid_answer_options(self):
        """Test that invalid answer options are rejected."""
        invalid_options = ["E", "F", "1", "2", "", " ", "AB", None]
        for option in invalid_options:
            assert validate_answer_option(option) is False, f"Option {option} should be invalid"


class TestInputValidation:
    """Test cases for input validation scenarios."""

    def test_empty_string_validation(self):
        """Test empty string handling."""
        assert validate_answer_option("") is False

    def test_whitespace_handling(self):
        """Test whitespace is not accepted as valid option."""
        assert validate_answer_option(" ") is False
        assert validate_answer_option("  ") is False

    def test_special_characters(self):
        """Test special characters are rejected."""
        special_chars = ["!", "@", "#", "$", "%"]
        for char in special_chars:
            assert validate_answer_option(char) is False

    def test_numeric_input(self):
        """Test numeric inputs are rejected."""
        for num in range(10):
            assert validate_answer_option(str(num)) is False


class TestAnswerComparison:
    """Test cases for answer comparison logic."""

    def test_case_insensitive_comparison(self):
        """Test answers are compared case-insensitively."""
        from app.services.scoring_service import is_answer_correct
        
        assert is_answer_correct("A", "A") is True
        assert is_answer_correct("a", "A") is True
        assert is_answer_correct("A", "a") is True
        assert is_answer_correct("a", "a") is True

    def test_different_answers(self):
        """Test different answers return False."""
        from app.services.scoring_service import is_answer_correct
        
        assert is_answer_correct("A", "B") is False
        assert is_answer_correct("C", "D") is False
        assert is_answer_correct("B", "A") is False

    def test_null_answer_handling(self):
        """Test null/None answer handling."""
        from app.services.scoring_service import is_answer_correct
        
        assert is_answer_correct(None, "A") is False
        assert is_answer_correct("", "A") is False
