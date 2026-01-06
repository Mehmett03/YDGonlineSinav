"""
E2E Test Scenario 04: Admin Adds Questions
Tests that an admin can add questions to an exam.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from tests.e2e.conftest import login_as_admin


class TestAdminAddQuestions:
    """Test admin adding questions to exam."""

    def test_add_question_to_exam(self, driver, base_url):
        """Test admin can add a question to an exam."""
        # Login and create exam first
        login_as_admin(driver, base_url)
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/dashboard")
        )
        
        # Create a new exam
        driver.get(f"{base_url}/admin/exam/create")
        
        driver.find_element(By.ID, "title").send_keys("Soru Ekleme Testi")
        duration = driver.find_element(By.ID, "duration_minutes")
        duration.clear()
        duration.send_keys("30")
        
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for questions page
        WebDriverWait(driver, 10).until(
            EC.url_contains("/questions")
        )
        
        # Add a question
        driver.find_element(By.ID, "question_text").send_keys("Python'da değişken tanımlamak için hangi anahtar kelime kullanılır?")
        driver.find_element(By.ID, "option_a").send_keys("var")
        driver.find_element(By.ID, "option_b").send_keys("let")
        driver.find_element(By.ID, "option_c").send_keys("Gerek yok")
        driver.find_element(By.ID, "option_d").send_keys("define")
        
        # Select correct answer
        correct_answer = Select(driver.find_element(By.ID, "correct_answer"))
        correct_answer.select_by_value("C")
        
        # Submit question
        driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
        
        # Wait for page refresh
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "question-card"))
        )
        
        # Verify question added
        page_source = driver.page_source
        assert "Python'da değişken" in page_source or "Soru 1" in page_source

    def test_add_multiple_questions(self, driver, base_url):
        """Test adding multiple questions to an exam."""
        login_as_admin(driver, base_url)
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/dashboard")
        )
        
        # Create exam
        driver.get(f"{base_url}/admin/exam/create")
        driver.find_element(By.ID, "title").send_keys("Çoklu Soru Testi")
        duration = driver.find_element(By.ID, "duration_minutes")
        duration.clear()
        duration.send_keys("60")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("/questions")
        )
        
        # Add 3 questions
        for i in range(3):
            driver.find_element(By.ID, "question_text").send_keys(f"Test Sorusu {i+1}?")
            driver.find_element(By.ID, "option_a").send_keys(f"Cevap A-{i+1}")
            driver.find_element(By.ID, "option_b").send_keys(f"Cevap B-{i+1}")
            driver.find_element(By.ID, "option_c").send_keys(f"Cevap C-{i+1}")
            driver.find_element(By.ID, "option_d").send_keys(f"Cevap D-{i+1}")
            
            correct = Select(driver.find_element(By.ID, "correct_answer"))
            correct.select_by_value("A")
            
            driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
            
            # Wait for refresh
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "question-card"))
            )
        
        # Verify all questions added
        question_cards = driver.find_elements(By.CLASS_NAME, "question-card")
        assert len(question_cards) >= 3
