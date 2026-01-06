"""
Selenium E2E test configuration and fixtures.
"""
import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# Base URL for the application
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")

# Selenium Grid URL (for Docker)
SELENIUM_URL = os.getenv("SELENIUM_URL", None)


@pytest.fixture(scope="function")
def driver():
    """Create a Selenium WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    if SELENIUM_URL:
        # Use Selenium Grid (Docker)
        driver = webdriver.Remote(
            command_executor=SELENIUM_URL,
            options=chrome_options
        )
    else:
        # Use local ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture
def base_url():
    """Return the base URL for tests."""
    return BASE_URL


def login_as_admin(driver, base_url):
    """Helper function to login as admin."""
    driver.get(f"{base_url}/auth/login-page")
    
    username_field = driver.find_element("id", "username")
    password_field = driver.find_element("id", "password")
    
    username_field.send_keys("admin")
    password_field.send_keys("admin123")
    
    submit_button = driver.find_element("css selector", "button[type='submit']")
    submit_button.click()


def login_as_student(driver, base_url, username="test_student", password="student123"):
    """Helper function to login as student."""
    driver.get(f"{base_url}/auth/login-page")
    
    username_field = driver.find_element("id", "username")
    password_field = driver.find_element("id", "password")
    
    username_field.send_keys(username)
    password_field.send_keys(password)
    
    submit_button = driver.find_element("css selector", "button[type='submit']")
    submit_button.click()


def register_student(driver, base_url, username, email, full_name, password):
    """Helper function to register a new student."""
    driver.get(f"{base_url}/auth/register-page")
    
    driver.find_element("id", "full_name").send_keys(full_name)
    driver.find_element("id", "username").send_keys(username)
    driver.find_element("id", "email").send_keys(email)
    driver.find_element("id", "password").send_keys(password)
    driver.find_element("id", "password_confirm").send_keys(password)
    
    driver.find_element("css selector", "button[type='submit']").click()
