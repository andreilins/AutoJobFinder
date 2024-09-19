import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv("credentials.env")

# Retrieve LinkedIn credentials
email = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")

# Verify credentials are loaded
if email is None or password is None:
    print("Environment variables are not set properly.")
    exit(1)

# Set up WebDriver
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

try:
    # Navigate to LinkedIn login page
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

    # Wait for and click the desired element using CSS Selector
    css_selector = 'li.global-nav__primary-item:nth-child(3)'
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
    )
    element.click()
    print("Clicked on the element.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    print("scoobydoo")
    