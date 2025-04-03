import os
import pandas as pd
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = "*****"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

def extract_results():
    """Extract verification results from CSV using pandas."""
    input_path = os.path.join("csv_files", "verification_results.csv")
    
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
    
    pirated_files = df[~df["gemini_verification"].astype(str).str.strip().isin(["0", "1"])].head(7)
    
    if not pirated_files.empty:
        output_path = os.path.join("csv_files", "pirated_files.csv")
        pirated_files.to_csv(output_path, index=False)
        print(f"Identified {len(pirated_files)} potentially pirated files. Results saved to {output_path}.")
    else:
        print("No pirated files identified.")
    
    return pirated_files.to_dict(orient='records')

extract_results()
print(checker())
