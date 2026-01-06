"""
E2E Test Scenario 03: Admin Creates Exam
Tests that an admin can create a new exam.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.e2e.conftest import login_as_admin


class TestAdminCreateExam:
    """Test admin exam creation scenario."""

    def test_admin_creates_exam(self, driver, base_url):
        """Test admin can create a new exam."""
        # Login as admin
        login_as_admin(driver, base_url)
        
        # Wait for dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/dashboard")
        )
        
        # Navigate to create exam page
        create_button = driver.find_element(By.LINK_TEXT, "Yeni Sınav")
        create_button.click()
        
        # Wait for create page
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/exam/create")
        )
        
        # Fill exam form
        title_field = driver.find_element(By.ID, "title")
        description_field = driver.find_element(By.ID, "description")
        duration_field = driver.find_element(By.ID, "duration_minutes")
        
        title_field.send_keys("Selenium Test Sınavı")
        description_field.send_keys("Bu sınav Selenium ile oluşturuldu")
        
        # Clear and set duration
        duration_field.clear()
        duration_field.send_keys("45")
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for redirect to questions page
        WebDriverWait(driver, 10).until(
            EC.url_contains("/questions")
        )
        
        # Verify on questions page with exam title
        page_source = driver.page_source
        assert "Selenium Test Sınavı" in page_source

    def test_exam_appears_on_dashboard(self, driver, base_url):
        """Test that created exam appears on admin dashboard."""
        # First create an exam
        login_as_admin(driver, base_url)
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/dashboard")
        )
        
        # Navigate to create
        driver.get(f"{base_url}/admin/exam/create")
        
        # Create exam
        driver.find_element(By.ID, "title").send_keys("Dashboard Test Sınavı")
        duration_field = driver.find_element(By.ID, "duration_minutes")
        duration_field.clear()
        duration_field.send_keys("30")
        
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Go back to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/questions")
        )
        
        driver.get(f"{base_url}/admin/dashboard")
        
        # Verify exam is listed
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "exam-card"))
        )
        
        page_source = driver.page_source
        assert "Dashboard Test Sınavı" in page_source
