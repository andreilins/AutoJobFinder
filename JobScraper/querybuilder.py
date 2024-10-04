#combines job descriptions and locations into one text file
#make a text file of job descriptions, one for each line. Then once you're done make an empty line and list countries
#that text file will be the argument for this script

import argparse

def process_jobs_and_countries(file_path):
    try:
        # Read the content of the file
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Split the lines into jobs and countries
        job_titles = []
        countries = []
        separator_found = False
        
        for line in lines:
            line = line.strip()
            if line:  # Ignore empty lines
                if not separator_found:
                    # Check if the line is likely a job title (can be adjusted)
                    job_titles.append(line)
                else:
                    countries.append(line)
            else:
                # If we encounter an empty line, we set the flag for countries
                separator_found = True
        
        # Debugging: Print the identified job titles and countries
        print("Job Titles Found:", job_titles)
        print("Countries Found:", countries)
        
        # Create output lines in the desired format
        output_lines = []
        for job in job_titles:
            for country in countries:
                output_lines.append(f"{job}:{country}")
        
        # Write the output to a new file
        output_file_path = 'output.txt'
        with open(output_file_path, 'w') as output_file:
            for item in output_lines:
                output_file.write(f"{item}\n")
        
        print(f"Processed data written to '{output_file_path}'")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process a text file with job titles and countries.")
    parser.add_argument("file_path", type=str, help="Path to the input text file")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the function with the provided file path
    process_jobs_and_countries(args.file_path)