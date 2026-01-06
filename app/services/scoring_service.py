"""
Scoring service for exam evaluation.
This module contains the core scoring logic that will be unit tested.
"""
from typing import List, Tuple
from datetime import datetime, timedelta

from app.models.question import Question
from app.models.result import ExamAttempt, UserAnswer


def calculate_score(user_answers: List[UserAnswer], questions: List[Question]) -> Tuple[float, int, int]:
    """
    Calculate the exam score based on user answers.
    
    Args:
        user_answers: List of user's submitted answers
        questions: List of exam questions
    
    Returns:
        Tuple of (score_percentage, correct_count, total_questions)
    
    Example:
        >>> answers = [UserAnswer(question_id=1, selected_answer="A")]
        >>> questions = [Question(id=1, correct_answer="A")]
        >>> calculate_score(answers, questions)
        (100.0, 1, 1)
    """
    if not questions:
        return 0.0, 0, 0
    
    total_questions = len(questions)
    correct_count = 0
    total_points = 0
    earned_points = 0
    
    # Create a mapping of question_id to question for quick lookup
    question_map = {q.id: q for q in questions}
    
    # Create a mapping of question_id to answer
    answer_map = {a.question_id: a.selected_answer for a in user_answers}
    
    for question in questions:
        total_points += question.points
        user_answer = answer_map.get(question.id)
        
        if user_answer and question.correct_answer.value == user_answer.upper():
            correct_count += 1
            earned_points += question.points
    
    # Calculate percentage score
    score_percentage = (earned_points / total_points * 100) if total_points > 0 else 0.0
    
    return round(score_percentage, 2), correct_count, total_questions


def is_answer_correct(user_answer: str, correct_answer: str) -> bool:
    """
    Check if a single answer is correct.
    
    Args:
        user_answer: The answer submitted by the user (A, B, C, or D)
        correct_answer: The correct answer
    
    Returns:
        True if the answer is correct, False otherwise
    
    Example:
        >>> is_answer_correct("A", "A")
        True
        >>> is_answer_correct("a", "A")
        True
        >>> is_answer_correct("B", "A")
        False
    """
    if not user_answer:
        return False
    return user_answer.upper() == correct_answer.upper()


def calculate_time_remaining(started_at: datetime, duration_minutes: int) -> int:
    """
    Calculate the remaining time for an exam attempt.
    
    Args:
        started_at: When the exam attempt started
        duration_minutes: Total exam duration in minutes
    
    Returns:
        Remaining time in seconds (0 if time has expired)
    
    Example:
        >>> from datetime import datetime, timedelta
        >>> started = datetime.utcnow() - timedelta(minutes=10)
        >>> calculate_time_remaining(started, 30)
        1200  # 20 minutes remaining in seconds
    """
    elapsed = datetime.utcnow() - started_at
    total_duration = timedelta(minutes=duration_minutes)
    remaining = total_duration - elapsed
    
    # Return 0 if time has expired
    seconds_remaining = int(remaining.total_seconds())
    return max(0, seconds_remaining)


def is_exam_expired(started_at: datetime, duration_minutes: int) -> bool:
    """
    Check if an exam attempt has expired.
    
    Args:
        started_at: When the exam attempt started
        duration_minutes: Total exam duration in minutes
    
    Returns:
        True if the exam time has expired, False otherwise
    
    Example:
        >>> from datetime import datetime, timedelta
        >>> started = datetime.utcnow() - timedelta(minutes=35)
        >>> is_exam_expired(started, 30)
        True
    """
    return calculate_time_remaining(started_at, duration_minutes) <= 0


def validate_answer_option(answer: str) -> bool:
    """
    Validate that an answer option is valid (A, B, C, or D).
    
    Args:
        answer: The answer to validate
    
    Returns:
        True if valid, False otherwise
    
    Example:
        >>> validate_answer_option("A")
        True
        >>> validate_answer_option("E")
        False
        >>> validate_answer_option("")
        False
    """
    if not answer:
        return False
    return answer.upper() in ["A", "B", "C", "D"]


def get_grade_letter(score: float) -> str:
    """
    Convert a numerical score to a letter grade.
    
    Args:
        score: The score percentage (0-100)
    
    Returns:
        Letter grade (AA, BA, BB, CB, CC, DC, DD, FF)
    
    Example:
        >>> get_grade_letter(95)
        'AA'
        >>> get_grade_letter(45)
        'FF'
    """
    if score >= 90:
        return "AA"
    elif score >= 85:
        return "BA"
    elif score >= 80:
        return "BB"
    elif score >= 75:
        return "CB"
    elif score >= 70:
        return "CC"
    elif score >= 65:
        return "DC"
    elif score >= 60:
        return "DD"
    else:
        return "FF"
