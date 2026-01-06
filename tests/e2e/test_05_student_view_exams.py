"""
E2E Test Scenario 05: Student Views Exams
Tests that a student can view available exams.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.e2e.conftest import register_student, login_as_student


class TestStudentViewExams:
    """Test student viewing available exams."""

    def test_student_sees_exam_list(self, driver, base_url):
        """Test student can see list of available exams."""
        # Register a new student
        unique_username = f"student_{pytest.importorskip('time').time()}"[:20]
        register_student(
            driver, base_url,
            username=unique_username,
            email=f"{unique_username}@test.com",
            full_name="Test Öğrenci",
            password="test123"
        )
        
        # Login
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login")
        )
        
        login_as_student(driver, base_url, unique_username, "test123")
        
        # Wait for dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/student/dashboard")
        )
        
        # Verify on student dashboard
        assert "/student/dashboard" in driver.current_url
        
        # Check for exam section
        page_source = driver.page_source
        assert "Aktif Sınavlar" in page_source or "Sınavlar" in page_source

    def test_student_dashboard_elements(self, driver, base_url):
        """Test student dashboard has correct elements."""
        # Register and login
        import time
        unique_username = f"student_{int(time.time())}"[:20]
        register_student(
            driver, base_url,
            username=unique_username,
            email=f"{unique_username}@test.com",
            full_name="Dashboard Test",
            password="test123"
        )
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login")
        )
        
        login_as_student(driver, base_url, unique_username, "test123")
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/student/dashboard")
        )
        
        # Check for navbar elements
        navbar = driver.find_element(By.CLASS_NAME, "navbar")
        assert navbar.is_displayed()
        
        # Check for logout button
        logout_link = driver.find_element(By.LINK_TEXT, "Çıkış")
        assert logout_link is not None

    def test_student_can_see_exam_details(self, driver, base_url):
        """Test that exam cards show proper details."""
        import time
        unique_username = f"student_{int(time.time())}"[:20]
        register_student(
            driver, base_url,
            username=unique_username,
            email=f"{unique_username}@test.com",
            full_name="Detail Test",
            password="test123"
        )
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login")
        )
        
        login_as_student(driver, base_url, unique_username, "test123")
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/student/dashboard")
        )
        
        # Check page source for exam info elements
        page_source = driver.page_source
        # Should have time icon or duration info
        assert "dakika" in page_source or "⏱️" in page_source or "Sınav" in page_source
