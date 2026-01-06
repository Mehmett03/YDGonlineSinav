"""
Unit tests for timer and time-related functions.
Tests exam duration and expiry logic.
"""
import pytest
from datetime import datetime, timedelta
from app.services.scoring_service import (
    calculate_time_remaining,
    is_exam_expired
)


class TestCalculateTimeRemaining:
    """Test cases for calculate_time_remaining function."""

    def test_full_time_remaining(self):
        """Test when exam just started."""
        started_at = datetime.utcnow()
        duration = 30  # minutes
        
        remaining = calculate_time_remaining(started_at, duration)
        
        # Should have approximately 30 minutes (1800 seconds)
        assert 1795 <= remaining <= 1800

    def test_half_time_remaining(self):
        """Test when half the time has elapsed."""
        started_at = datetime.utcnow() - timedelta(minutes=15)
        duration = 30
        
        remaining = calculate_time_remaining(started_at, duration)
        
        # Should have approximately 15 minutes (900 seconds)
        assert 895 <= remaining <= 905

    def test_time_expired(self):
        """Test when time has completely expired."""
        started_at = datetime.utcnow() - timedelta(minutes=35)
        duration = 30
        
        remaining = calculate_time_remaining(started_at, duration)
        
        assert remaining == 0

    def test_just_expired(self):
        """Test when time just expired."""
        started_at = datetime.utcnow() - timedelta(minutes=30, seconds=1)
        duration = 30
        
        remaining = calculate_time_remaining(started_at, duration)
        
        assert remaining == 0

    def test_one_minute_remaining(self):
        """Test with one minute remaining."""
        started_at = datetime.utcnow() - timedelta(minutes=29)
        duration = 30
        
        remaining = calculate_time_remaining(started_at, duration)
        
        # Should have approximately 1 minute (60 seconds)
        assert 55 <= remaining <= 65

    def test_negative_time_returns_zero(self):
        """Test that negative remaining time returns 0."""
        started_at = datetime.utcnow() - timedelta(hours=2)
        duration = 30
        
        remaining = calculate_time_remaining(started_at, duration)
        
        assert remaining == 0


class TestIsExamExpired:
    """Test cases for is_exam_expired function."""

    def test_not_expired_at_start(self):
        """Test exam is not expired when just started."""
        started_at = datetime.utcnow()
        duration = 30
        
        assert is_exam_expired(started_at, duration) is False

    def test_not_expired_mid_exam(self):
        """Test exam is not expired during exam."""
        started_at = datetime.utcnow() - timedelta(minutes=15)
        duration = 30
        
        assert is_exam_expired(started_at, duration) is False

    def test_expired_after_duration(self):
        """Test exam is expired after duration."""
        started_at = datetime.utcnow() - timedelta(minutes=31)
        duration = 30
        
        assert is_exam_expired(started_at, duration) is True

    def test_expired_exactly_at_duration(self):
        """Test exam is expired exactly at duration."""
        started_at = datetime.utcnow() - timedelta(minutes=30)
        duration = 30
        
        # At exactly 30 minutes, remaining should be 0 or very close to it
        assert is_exam_expired(started_at, duration) is True

    def test_not_expired_just_before_end(self):
        """Test exam is not expired just before end."""
        started_at = datetime.utcnow() - timedelta(minutes=29, seconds=30)
        duration = 30
        
        assert is_exam_expired(started_at, duration) is False


class TestTimerEdgeCases:
    """Test edge cases for timer functionality."""

    def test_very_short_exam(self):
        """Test with very short exam duration (5 minutes)."""
        started_at = datetime.utcnow()
        duration = 5
        
        remaining = calculate_time_remaining(started_at, duration)
        assert 295 <= remaining <= 300  # ~5 minutes

    def test_very_long_exam(self):
        """Test with long exam duration (180 minutes)."""
        started_at = datetime.utcnow()
        duration = 180
        
        remaining = calculate_time_remaining(started_at, duration)
        assert 10795 <= remaining <= 10800  # ~3 hours

    def test_zero_duration(self):
        """Test with zero duration (edge case)."""
        started_at = datetime.utcnow()
        duration = 0
        
        remaining = calculate_time_remaining(started_at, duration)
        assert remaining == 0
        assert is_exam_expired(started_at, duration) is True

    def test_future_start_time(self):
        """Test with future start time (shouldn't happen but handle gracefully)."""
        started_at = datetime.utcnow() + timedelta(minutes=5)
        duration = 30
        
        # Should show full duration + extra time
        remaining = calculate_time_remaining(started_at, duration)
        assert remaining > 1800  # More than 30 minutes
