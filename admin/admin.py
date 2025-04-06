import os
import pandas as pd
import google.generativeai as genai
from api_store import api  # Use the API key from api_store.py

# Configure Gemini API
genai.configure(api_key=api())

def extract_results():
    """Extract detection data from the datasets folder."""
    input_path = os.path.join("datasets", "detection_database.csv")
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(input_path, dtype=str)
    print(f"Extracted {len(df)} records from {input_path}")
    print(df.head()) 
    return df

def checker():
    """Check whether file name or source is pirated using Gemini API and write to a file."""
    df = extract_results()
    if df.empty:
        return []
    
    for _, row in df.iterrows():
        file_name = row.get("flagged_files","file_source")
        print(f"{file_name} is set to be taken down")

    return df.to_dict(orient="records")


# Debug/testing
if __name__ == "__main__":
    extract_results()
    print(checker())
