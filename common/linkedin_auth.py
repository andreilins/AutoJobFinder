import pickle
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def save_cookies(driver, path):
    with open(path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, path):
    with open(path, "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

# Function to check if cookies exist
def cookies_exist(path):
    return os.path.exists(path)

def authenticate(driver):
    COOKIE_FILE = "cookies.pkl"

    # Load environment variables
    load_dotenv("credentials.env")

    # Retrieve LinkedIn credentials
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")

    # Verify credentials are loaded
    if email is None or password is None:
        print("Environment variables are not set properly.")
        exit(1)

    # Navigate to LinkedIn login page
    driver.get("https://www.linkedin.com")

    if cookies_exist(COOKIE_FILE):
        print("Loading cookies...")
        load_cookies(driver, COOKIE_FILE)
        driver.get("https://www.linkedin.com/feed/")
    
        # Wait to verify if session is valid
        try:
            WebDriverWait(driver, 10).until(
                EC.url_contains("feed")
            )
            print("Successfully loaded session from cookies")
            return
        except:
            print("Session cookies are expired or invalid. Logging in again.")

    # Perform normal login if cookies don't exist or are invalid
    print("Performing normal login...")
    driver.get("https://www.linkedin.com/login")

    # Wait for login page to load and enter credentials
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    email_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    email_field.send_keys(email)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    # Wait for login to complete
    WebDriverWait(driver, 10).until(
        EC.url_contains("feed")
    )
    print("Login successful!")
    
    save_cookies(driver, "cookies.pkl")
    print("Session cookies saved")