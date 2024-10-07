import os
import argparse
import pickle
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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


def search_jobs(driver, job_title, location):
    try:

        wait = WebDriverWait(driver, 10)

        location_input = driver.find_element("css selector", "[data-job-search-box-location-input-trigger]")
        search_button = driver.find_element("css selector", "button.jobs-search-box__submit-button.artdeco-button")

        # Get the value of the attribute
        location_value = location_input.get_attribute("data-job-search-box-location-input-trigger")

        # Use an if statement to check for a specific value
        if location_value != location:
            # Find and fill the location input
            location_input = driver.find_element(By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")
            location_input.send_keys(Keys.CONTROL + "a")
            location_input.send_keys(Keys.BACKSPACE)
            location_input.send_keys(location)
            search_button.click()

            time.sleep(3)

        # Find and fill the job title input
        job_input = driver.find_element(By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")
        job_input.send_keys(Keys.CONTROL + "a")
        job_input.send_keys(Keys.BACKSPACE)
        job_input.send_keys(job_title)
        search_button.click()

        print(f"{job_title} in {location}:")

        time.sleep(3)

        try:
            no_jobs_message = driver.find_element(By.CSS_SELECTOR, "h1.t-24.t-black.t-normal.text-align-center")
            if "No matching jobs found." in no_jobs_message.text:
                print("0 results")
                return  # Exit the function if the message is found
        except Exception as e:
            pass

        elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jobs-search-results-list__subtitle')))

        for element in elements:
            # Find the span inside the element (no extra wait is needed)
            span = element.find_element(By.TAG_NAME, 'span')
            print(span.text)
        
        navigateList(driver)

        time.sleep(3)

    except Exception as e:
        print(f"An error occurred during job search: {e}")

def navigateList(driver):
    # Locate the job list container
    job_list_container = driver.find_element(By.CSS_SELECTOR, "ul.scaffold-layout__list-container")
    
    # Initialize a set to keep track of already clicked jobs
    clicked_jobs = set()
    
    # Keep track of the previous number of job items
    previous_job_count = 0

    while True:
        # Locate all individual job items (div elements that contain each job card)
        job_items = job_list_container.find_elements(By.CSS_SELECTOR, "div.job-card-container")
        
        # Check if new jobs have been loaded
        if len(job_items) == previous_job_count:
            break  # Exit loop if no new jobs are found
        
        # Update the count of job items
        previous_job_count = len(job_items)

        # Iterate over each job item
        for job in job_items:
            job_id = job.get_attribute("data-job-id")  # Replace with actual identifier if available
            if job_id not in clicked_jobs:
                try:
                    # Click on the job
                    job.click()
                    clicked_jobs.add(job_id)  # Add to clicked jobs to prevent re-clicking
                    print(f"Clicked on job: {job_id}")

                    # Wait for 1 second
                    time.sleep(1)

                    # Scroll down to the next job (simulate moving to the next job)
                    driver.execute_script("arguments[0].scrollIntoView();", job)
                    time.sleep(1)  # wait for any potential animations or loading

                except Exception as e:
                    print(f"An error occurred while clicking on job: {e}")
            
            # Optional: Break if you want to limit the number of jobs clicked
            if len(clicked_jobs) >= 25:  # Limit to clicking 25 jobs, for example
                break

def extractInfo(driver):
    company_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-details-jobs-unified-top-card__company-name a"))
    )

    # Extract the company name (text inside the <a> tag)
    company_name = company_element.text

    print(f"Company Name: {company_name}")

    job_element = driver.find_element(By.CSS_SELECTOR, 'h1.t-24.t-bold.inline a')

    job_name = job_element.text
    job_link = job_element.get_attribute("href")

    print(f"Job Name: {job_name}")
    print(f"Job Link: {job_link}")

    # Locate the element and extract the location text
    location_element = driver.find_element(By.CSS_SELECTOR, "div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text")

    # Extract the location part (everything before the '·')
    location = location_element.text.split("·")[0].strip()

    print(f"Location: {location}")

    # Locate the div containing the apply button
    apply_button_div = driver.find_element("css selector", "div.jobs-apply-button--top-card")

    # Try to locate the <span> element inside the apply button div
    apply_type_element = apply_button_div.find_element("css selector", "span.artdeco-button__text")

    # Extract the text from the <span> tag
    apply_type = apply_type_element.text.strip()  # Use strip to remove extra whitespace

    easy_apply = False

    if apply_type == "Easy Apply":
        easy_apply = True
    elif apply_type == "Apply":
        easy_apply = False
    
    print(f"Easy Apply: {easy_apply}")

    # Locate the <article> element by its class name
    job_description_element = driver.find_element("css selector", "article.jobs-description__container")

    # Extract the text content from the <article> element
    job_description = job_description_element.text

    print(f"Job Description: {job_description}")

def main(file_path):

    # Set up WebDriver
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

    try:
        authenticate(driver)
        driver.get("https://www.linkedin.com/jobs/search/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']"))
        )

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Loop through each line and split by ":"
            for line in lines:
                line = line.strip()  # Remove leading/trailing whitespace
                if ':' in line:
                    location, job_title = line.split(':', 1)  # Split by first occurrence of ":"
                    location = location.strip()
                    job_title = job_title.strip()
                    
                    # Call the search_jobs function
                    search_jobs(driver, job_title, location)
                else:
                    print(f"Skipping line: '{line}' (not in 'job:location' format)")
        
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process a text file.")
    parser.add_argument("file_path", type=str, help="Path to the text file to be processed")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the main function with the provided file path
    main(args.file_path)

    