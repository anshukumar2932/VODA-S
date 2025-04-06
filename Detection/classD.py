import os
import csv
import hashlib
import random
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = "******"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

dataset_path = os.path.join("csv_files", "dataset.csv")
text_files_path = "text_files"

def compute_sha256(text):
    """Compute SHA-256 hash for content."""
    return hashlib.sha256(text.encode()).hexdigest()

def load_dataset():
    """Load dataset hashes, sources, and labels from CSV."""
    dataset = {}
    with open(dataset_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            dataset[row["hash"]] = {"source": row["source"], "label": row["label"]}
    return dataset

def check_with_gemini(content):
    """Use Gemini AI to check if the content is pirated."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Is this text legally distributed? Answer 0 for yes, 1 for no, or 2 for maybe: {content}")
        return response.text.strip()
    except Exception as e:
        print (f"Error with Gemini API: {e}")
        return f"Error with Gemini API: {e}"

def verify_files():
    """Randomly select 10 files and verify against dataset and Gemini AI."""
    dataset_hashes = load_dataset()
    results = []

    # Get a list of all text files and randomly pick 10
    all_files = os.listdir(text_files_path)
    selected_files = random.sample(all_files, min(10, len(all_files)))

    for file_name in selected_files:
        file_path = os.path.join(text_files_path, file_name)

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        file_hash = compute_sha256(content)

        # Check dataset for a match
        source = dataset_hashes.get(file_hash, {}).get("source", "Unknown")
        label = dataset_hashes.get(file_hash, {}).get("label", "Unverified")

        # Gemini AI verification
        gemini_result = check_with_gemini(content)

        results.append({
            "file_name": file_name,
            "hash": file_hash,
            "source": source,
            "dataset_label": label,
            "gemini_verification": gemini_result
        })

    return results

def save_results(results):
    """Save verification results to CSV."""
    output_path = os.path.join("csv_files", "verification_results.csv")

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["file_name", "hash", "source", "dataset_label", "gemini_verification"])
        writer.writeheader()
        writer.writerows(results)

    print(f" Verification results saved in {output_path}")

# Run verification for 10 random files
results = verify_files()
save_results(results)
