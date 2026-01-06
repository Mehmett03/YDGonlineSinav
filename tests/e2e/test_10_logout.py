"""
E2E Test Scenario 10: Logout
Tests that users can successfully log out.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.e2e.conftest import login_as_admin


class TestLogout:
    """Test logout functionality."""

    def test_admin_logout(self, driver, base_url):
        """Test admin can logout successfully."""
        # Login as admin
        login_as_admin(driver, base_url)
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/dashboard")
        )
        
        # Click logout
        logout_button = driver.find_element(By.LINK_TEXT, "Çıkış")
        logout_button.click()
        
        # Wait for redirect to login
        WebDriverWait(driver, 10).until(
            EC.url_contains("/auth/login")
        )
        
        # Verify on login page
        assert "/auth/login" in driver.current_url

    def test_logout_clears_session(self, driver, base_url):
        """Test that logout clears the session cookie."""
        # Login
        login_as_admin(driver, base_url)
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/dashboard")
        )
        
        # Logout
        driver.find_element(By.LINK_TEXT, "Çıkış").click()
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/auth/login")
        )
        
        # Try to access protected page
        driver.get(f"{base_url}/admin/dashboard")
        
        # Should redirect to login
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login")
        )
        
        assert "/login" in driver.current_url

    def test_student_logout(self, driver, base_url):
        """Test student can logout successfully."""
        # Register a new student
        import time
        unique = f"logout_{int(time.time())}"[:20]
        
        driver.get(f"{base_url}/auth/register-page")
        driver.find_element(By.ID, "full_name").send_keys("Logout Test")
        driver.find_element(By.ID, "username").send_keys(unique)
        driver.find_element(By.ID, "email").send_keys(f"{unique}@test.com")
        driver.find_element(By.ID, "password").send_keys("test123")
        driver.find_element(By.ID, "password_confirm").send_keys("test123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login")
        )
        
        # Login
        driver.find_element(By.ID, "username").send_keys(unique)
        driver.find_element(By.ID, "password").send_keys("test123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/student/dashboard")
        )
        
        # Logout
        logout_button = driver.find_element(By.LINK_TEXT, "Çıkış")
        logout_button.click()
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login")
        )
        
        assert "/login" in driver.current_url

    def test_logout_from_navbar(self, driver, base_url):
        """Test logout button is accessible from navbar."""
        login_as_admin(driver, base_url)
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/dashboard")
        )
        
        # Verify logout is in navbar
        navbar = driver.find_element(By.CLASS_NAME, "navbar")
        logout_link = navbar.find_element(By.LINK_TEXT, "Çıkış")
        
        assert logout_link.is_displayed()
        
        # Click and verify
        logout_link.click()
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login")
        )
