from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import time

# Step 1: Set up the WebDriver (this will automatically install the appropriate GeckoDriver)
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

# Step 2: Navigate to a website (e.g., Google)
driver.get("https://www.google.com")

# Step 3: Print the page title
print("Page title is:", driver.title)

# Optional: Find an element (Google search bar) and interact with it
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("Hello World!")
search_box.submit()  # Submit the search form

# Optional: Wait for a while to see the results
time.sleep(5)

# Close the browser after executing the commands
driver.quit()
