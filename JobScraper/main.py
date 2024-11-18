import argparse
import time
import sqlite3
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import sys
sys.path.append("..")
from common.linkedin_auth import *

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
    clicked_jobs = set()  # Set to keep track of already clicked jobs
    job_list = []
    
    while True:
        # Restart the process of scrolling and collecting job items on the current page
        while True:
            try:
                # Locate the job list container and its items
                job_list_container = driver.find_element(By.CSS_SELECTOR, "ul.scaffold-layout__list-container")
                job_items = job_list_container.find_elements(By.CSS_SELECTOR, "div.job-card-container")
                
                # Process each job card
                for job in job_items:
                    job_id = job.get_attribute("data-job-id")  # Replace with actual identifier if available
                    if job_id not in clicked_jobs:
                        try:
                            # Click on the job card
                            job.click()
                            clicked_jobs.add(job_id)
                            time.sleep(1)  # Wait a bit to simulate human interaction
                            job_list.append(extractInfo(driver, job_id))  # Extract info from the clicked job card and add to job list
                            
                            # Scroll to the clicked job
                            driver.execute_script("arguments[0].scrollIntoView();", job)
                            time.sleep(1)  # Wait for any loading or animation

                        except Exception as e:
                            print(f"An error occurred while clicking on job: {e}")
                
                # After processing all loaded jobs, check if there are more jobs to scroll to
                # Scroll down to load more jobs (if applicable)
                last_job = job_items[-1]  # Get the last job card
                driver.execute_script("arguments[0].scrollIntoView();", last_job)
                time.sleep(2)  # Wait for the new jobs to load after scrolling

                # After scrolling, find the updated list of jobs
                updated_job_items = job_list_container.find_elements(By.CSS_SELECTOR, "div.job-card-container")
                
                # If no new jobs are loaded, break the inner loop to proceed to the next page
                # add the current page entries to the database and clear the list
                if len(updated_job_items) == len(job_items):
                    # Open connection to the same database
                    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'jobs.db')
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    # Insert the list of tuples into the database
                    cursor.executemany('''
                    INSERT OR IGNORE INTO jobs (id, title, company, location, description, url, easy_apply)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', job_list)

                    # Commit the transaction
                    conn.commit()

                    # Close the connection
                    conn.close()

                    print("Batch insertion completed.")

                    job_list = []

                    break  # No new jobs, move on to pagination
                
            except Exception as e:
                print(f"Error during job search on this page: {e}")
                break

        try:
            # Find the pagination container
            pagination_list = driver.find_element(By.CSS_SELECTOR, ".jobs-search-pagination__pages")
            
            # Locate the active page
            active_page = pagination_list.find_element(By.CSS_SELECTOR, ".jobs-search-pagination__indicator-button--active")

            parent_element = active_page.find_element(By.XPATH, "..")
            
            # Find the next page (next sibling of the active page)
            next_page = parent_element.find_element(By.XPATH, "following-sibling::li[1]")
            
            if next_page:
                # Click on the next page number
                next_page.click()
                time.sleep(2)  # Wait for the next page to load
                
                # Reset the set of clicked jobs for the new page
                clicked_jobs = set()  # Clear clicked jobs for new page processing
                
            else:
                print("No more pages available.")
                break  # Exit if there is no next page

        except Exception as e:
            print(f"No next page found or an error occurred: {e}")
            break  # Exit the loop if no pagination is found or an error occurs



def extractInfo(driver, job_id):
    company_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-details-jobs-unified-top-card__company-name a"))
    )

    # Extract the company name (text inside the <a> tag)
    company_name = company_element.text
    job_element = driver.find_element(By.CSS_SELECTOR, 'h1.t-24.t-bold.inline a')
    job_name = job_element.text
    job_link = job_element.get_attribute("href")
    location_element = driver.find_element(By.CSS_SELECTOR, "div.job-details-jobs-unified-top-card__primary-description-container span.tvm__text")
    location = location_element.text.split("·")[0].strip()
    apply_button_div = driver.find_element("css selector", "div.jobs-apply-button--top-card")
    apply_type_element = apply_button_div.find_element("css selector", "span.artdeco-button__text")
    apply_type = apply_type_element.text.strip()  # Use strip to remove extra whitespace

    easy_apply = False

    if apply_type == "Easy Apply":
        easy_apply = True
    elif apply_type == "Apply":
        easy_apply = False

    job_description_element = driver.find_element("css selector", "article.jobs-description__container")
    job_description = job_description_element.text
    print("|----------------------------------------------------|")
    print(f"Job Name: {job_name}")
    print(f"Company: {company_name}")
    print(f"Job ID: {job_id}")
    #print(f"Job Link: {job_link}")
    print(f"Location: {location}")
    print(f"Easy Apply: {easy_apply}")
    #print(f"Job Description: {job_description}")

    job = (job_id, job_name, company_name, location, job_description, job_link, easy_apply)

    return job

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
                    print(f"Skipping line: '{line}' (not in 'location:job' format)")
        
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

    