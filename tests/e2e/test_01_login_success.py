"""
E2E Test Scenario 01: Successful Login
Tests that a user can successfully log in with valid credentials.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestLoginSuccess:
    """Test successful login scenario."""

    def test_admin_login_success(self, driver, base_url):
        """Test admin can login with valid credentials."""
        # Navigate to login page
        driver.get(f"{base_url}/auth/login-page")
        
        # Verify on login page
        assert "Giriş" in driver.title or "Login" in driver.title
        
        # Fill login form
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for redirect
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/dashboard")
        )
        
        # Verify on admin dashboard
        assert "/admin/dashboard" in driver.current_url
        
        # Verify welcome message or user name is displayed
        page_source = driver.page_source
        assert "Sistem Yöneticisi" in page_source or "admin" in page_source.lower()

    def test_login_page_elements(self, driver, base_url):
        """Test that login page has all required elements."""
        driver.get(f"{base_url}/auth/login-page")
        
        # Check for username field
        username_field = driver.find_element(By.ID, "username")
        assert username_field.is_displayed()
        
        # Check for password field
        password_field = driver.find_element(By.ID, "password")
        assert password_field.is_displayed()
        
        # Check for submit button
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert submit_button.is_displayed()
        
        # Check for register link
        register_link = driver.find_element(By.LINK_TEXT, "Kayıt Olun")
        assert register_link.is_displayed()
