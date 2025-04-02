import os
import pandas as pd
import google.generativeai as gemini

gemini.configure(api_key="VODA-S")

def analyze_filename_with_nlp(filename):
    """
    Uses NLP to determine if the filename suggests pirated content.
    Returns 1 (pirated) or 0 (not pirated).
    """
    model = gemini.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(f"Does this filename indicate pirated content? Answer only 1 for Yes, 0 for No: {filename} ignore .txt extension as it's a test to detect filename.")

    try:
        result_text = response.text.strip() if hasattr(response, 'text') else response.candidates[0].content.strip()
        
        if result_text in ["0", "1"]:
            print(result_text)
            return int(result_text)
        else:
            print(f"Unexpected response from API: {result_text}")
            return 0  # Default to 'not pirated' if response is unclear
    except Exception as e:
        print(f"Error processing response: {e}")
        return 0  # Default to 'not pirated' in case of error

def process_files(base_folder):
    """
    Analyzes filenames instead of file content.
    """
    flagged_files = []
    
    for website in os.listdir(base_folder):
        site_path = os.path.join(base_folder, website)
        
        if os.path.isdir(site_path):  # Ensure it's a folder
            for file in os.listdir(site_path):
                file_path = os.path.join(site_path, file)

                try:
                    result = analyze_filename_with_nlp(file)  # Analyze the filename
                        
                    if result == 1:
                        flagged_files.append((file, website))  # Store flagged filenames
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return flagged_files

def send_to_verification(flagged_files, csv_path):
    """
    Stores flagged files into a CSV for Verification Class.
    """
    df = pd.DataFrame(flagged_files, columns=['filename', 'source'])
    df.to_csv(csv_path, index=False)
    print("Flagged files sent to Verification.")

if __name__ == "__main__":
    base_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Internet"))
    csv_output = os.path.abspath(os.path.join(os.getcwd(), "datasets", "observation_database.csv"))
    
    flagged = process_files(base_folder)
    send_to_verification(flagged, csv_output)
