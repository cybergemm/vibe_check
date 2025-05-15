from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)  # Set implicit wait timeout
    yield driver
    driver.quit()

def test_login_success(driver):
    driver.get('http://127.0.0.1:5000/login')
    username = driver.find_element(By.NAME, 'username')
    password = driver.find_element(By.NAME, 'password')
    username.send_keys('testuser')
    password.send_keys('password123')
    password.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.url_contains('/home'))
    assert 'Welcome' in driver.page_source

def test_login_failure(driver):
    driver.get('http://127.0.0.1:5000/login')
    username = driver.find_element(By.NAME, 'username')
    password = driver.find_element(By.NAME, 'password')
    username.send_keys('wronguser')
    password.send_keys('wrongpass')
    password.send_keys(Keys.RETURN)
    assert 'Invalid username or password' in driver.page_source

def test_signup_success(driver):
    driver.get('http://127.0.0.1:5000/signup')
    username = driver.find_element(By.NAME, 'username')
    password = driver.find_element(By.NAME, 'password')
    username.send_keys('newuser')
    password.send_keys('newpass')
    password.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.url_contains('/login'))
    assert 'Registration successful' in driver.page_source

def test_mood_entry(driver):
    driver.get('http://127.0.0.1:5000/login')
    username = driver.find_element(By.NAME, 'username')
    password = driver.find_element(By.NAME, 'password')
    username.send_keys('testuser')
    password.send_keys('password123')
    password.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.url_contains('/home'))
    mood_input = driver.find_element(By.NAME, 'mood')
    mood_input.send_keys('Happy')
    mood_input.send_keys(Keys.RETURN)
    assert 'Happy' in driver.page_source 
