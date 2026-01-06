"""
E2E Test Scenario 02: Login Failure
Tests that invalid credentials are properly rejected.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestLoginFailure:
    """Test login failure scenarios."""

    def test_wrong_password(self, driver, base_url):
        """Test login fails with wrong password."""
        driver.get(f"{base_url}/auth/login-page")
        
        # Fill login form with wrong password
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("wrongpassword")
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for error message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-error"))
        )
        
        # Verify error message
        error_message = driver.find_element(By.CLASS_NAME, "alert-error")
        assert "hatalı" in error_message.text.lower() or "error" in error_message.text.lower()
        
        # Verify still on login page
        assert "/auth/login" in driver.current_url

    def test_wrong_username(self, driver, base_url):
        """Test login fails with non-existent username."""
        driver.get(f"{base_url}/auth/login-page")
        
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.send_keys("nonexistentuser")
        password_field.send_keys("somepassword")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for error
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-error"))
        )
        
        # Still on login page
        assert "/auth/login" in driver.current_url

    def test_empty_credentials(self, driver, base_url):
        """Test login form validation with empty fields."""
        driver.get(f"{base_url}/auth/login-page")
        
        # Try to submit empty form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Form should not submit (HTML5 validation)
        # Check we're still on login page
        assert "/auth/login" in driver.current_url
