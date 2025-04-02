import os
import csv
import hashlib
import random
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = "*****"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

def extract_results():
    """Extract verification results from CSV."""
    input_path = os.path.join("csv_files", "verification_results.csv")
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return []
    
    with open(input_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        results = [row for row in reader]
    
    print(f"Extracted {len(results)} records from {input_path}")
    print(results)
    return results
def checker():
    "It check whether file name or source is pirated using Gemini api"
    results = extract_results()
    pirated_files = []
    count=0
    for record in results:
        count+=1
        if count>=8:
            break
        gemini_verification = str(record.get("gemini_verification", "")).strip()

        if gemini_verification not in ["0", "1"]:
            pirated_files.append(record)
    
    print(f"Identified {len(pirated_files)} potentially pirated files.")
    return pirated_files

extract_results()
print(checker())
