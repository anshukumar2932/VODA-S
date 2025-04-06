import os
import pandas as pd
import google.generativeai as gemini
from api_store import api
import time

gemini.configure(api_key="AIzaSyDarsGu_YMbE6qQbNblRPO9pplAeKhYGiI")

time.sleep(2)
# Paths
base_folder = os.path.abspath(os.path.join(os.getcwd(), "Internet"))
database_file = os.path.abspath(os.path.join(os.getcwd(), "datasets", "observation_database.csv"))
verification_output = os.path.abspath(os.path.join(os.getcwd(), "datasets", "verification_database.csv"))
expected_content_file = os.path.abspath(os.path.join(os.getcwd(), "datasets", "expected_content.csv"))

# Load datasets
observation_df = pd.read_csv(database_file)
expected_content_df = pd.read_csv(expected_content_file)

# Initialize result list
verified_files = []

def check_piracy(content, moviename, expected_content_df):
    """
    Compares content and moviename against expected dataset.
    """
    expected_list = expected_content_df.to_dict(orient='records')

    prompt = f"Does the following content match any legitimate movie content? Even slight variations should be considered" \
             f"Movie Name: {moviename} Content: {content}. " \
             f"Return 1 for yes, 0 for no. and only 1 or 0 in output."

    model = gemini.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    print(f"[CLASS_V>>>VERFYING]: Checking the current file {moviename} for the content...]")
    time.sleep(1)
    try:
        result_text = response.text.strip() if hasattr(response, 'text') else response.candidates[0].content.strip()
        if result_text in ["0", "1"]:
            return int(result_text)
        else:
            print(f"Unexpected response from API: {result_text}")
            return 0  # Default to 'not pirated' if response is unclear
    except Exception as e:
        print(f"Error processing response: {e}")
        return 0  # Default to 'not pirated' in case of error

# Process each file in observation data
for _, row in observation_df.iterrows():
    filename, source = row['filename'], row['source']
    file_path = os.path.join(base_folder, source, filename)

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()  # Read entire file
        
        # Extract moviename from filename (if applicable)
        moviename = filename.split('.')[0]  # Assuming filenames are like "movie_name.txt"

        # Check piracy using content and moviename
        piracy_flag = check_piracy(content, moviename, expected_content_df)

        if piracy_flag:
            verified_files.append([filename, source])
# Save results
verified_df = pd.DataFrame(verified_files, columns=["filename", "source"])
verified_df.to_csv(verification_output, index=False)
print("Verification process completed and saved.")
time.sleep(2)
