from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Set up WebDriver
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

# Navigate to the login page
driver.get("https://www.linkedin.com/login")
