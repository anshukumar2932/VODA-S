import os
import google.generativeai as gemini
import pandas as pd
import re
from api_store import api
import time

time.sleep(3)
gemini.configure(api_key="AIzaSyA-cwP57q6xPa7W5f6s16qKnksv7BRmv1A")

base_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Internet"))
verification_database = os.path.abspath(os.path.join(os.getcwd(), "datasets", "verification_database.csv"))
key_database = os.path.abspath(os.path.join(os.getcwd(), "datasets", "key_database.csv"))
detection_database_path = os.path.abspath(os.path.join(os.getcwd(), "datasets", "detection_database.csv"))
unclassified_database_path = os.path.abspath(os.path.join(os.getcwd(), "datasets", "unclassified_database.csv"))

class VerifiDataLoader:
    def __init__(self, base_dir=".."):
        self.base_dir = os.path.abspath(base_dir)
        self.dataset_path = verification_database
        self.data = None

    def load_data(self):
        try:
            self.data = pd.read_csv(self.dataset_path)
            return self.data
        except FileNotFoundError:
            print(f"[ERROR] verification_database.csv not found at {self.dataset_path}")
            return None
        except Exception as e:
            print(f"[ERROR] An error occurred while loading verification_database.csv: {e}")
            return None

def read_raw_txts(verifi_df, internet_folder=base_folder):
    raw_data = []
    for index, row in verifi_df.iterrows():
        filename = row[0]  # column index 0: filename
        source = row[1]    # column index 1: source (subfolder)

        file_path = os.path.join(internet_folder, source, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                raw_data.append({
                    'filename': filename,
                    'source': source,
                    'content': content
                })
        except FileNotFoundError:
            print(f"[WARN] File not found: {file_path}")
        except Exception as e:
            print(f"[ERROR] Failed to read {file_path}: {e}")
    return raw_data

class KeyDataLoader:
    def __init__(self, base_dir=".."):
        self.base_dir = os.path.abspath(base_dir)
        self.dataset_path = key_database
        self.data = None
    def load_data(self):
        try:
            self.data = pd.read_csv(self.dataset_path)
            return self.data
        except FileNotFoundError:
            print(f"[ERROR] verification_database.csv not found at {self.dataset_path}")
            return None
        except Exception as e:
            print(f"[ERROR] An error occurred while loading verification_database.csv: {e}")
            return None


def gemini_checks_source(source_value, legal_list, illegal_list):
    model = gemini.GenerativeModel("gemini-2.0-flash")
    prompt1 = f"check if the {source_value} is in either in {legal_list} or {illegal_list}. If it's in legal, then give only 0, If in illegal, then give 1 and if not in either then give 2. DO NOT GIVE ANYTHING ELSE other than number in output"
    response = model.generate_content(prompt1)
    try:
        print(f"[CLASS-D>>>DETECTING]: Checking the current file...")
        wait()
        result_source = response.text.strip() if hasattr(response, 'text') else response.candidates[0].content.strip()
        if result_source in ["0", "1", "2"]:
            return int(result_source)
        else:
            print(f"Unexpected response from API: {result_source}")
            return 0  # Default to 'not pirated' if response is unclear
    except Exception as e:
        print(f"Error processing response: {e}")
        return 0  # Default to 'not pirated' in case of error

def gemini_checks_key(key,keyidentifier):
    model = gemini.GenerativeModel("gemini-2.0-flash")
    prompt2 = f"Just give numerical output. check if the key_identity: {key} is in either in {keyidentifier} or not. Return only 1 for true and 0 for False"
    response = model.generate_content(prompt2)
    try:
        result_key = response.text.strip() if hasattr(response, 'text') else response.candidates[0].content.strip()
        if result_key in ["0", "1"]:
            return int(result_key)
        else:
            print(f"Unexpected response from API: {result_key}")
            return 0  # Default to 'not pirated' if response is unclear
    except Exception as e:
        print(f"Error processing response: {e}")
        return 0  # Default to 'not pirated' in case of error


def key_extractor(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith("key_identity:"):
                    return line.split(":", 1)[1].strip()
        return None
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None



def extract_key_identity(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('key_identity:'):
                return line.split(':', 1)[1].strip()  # Get the part after the colon and strip any whitespace
    
def Detection():
    filename_flag = []
    source_flag = []
    unclassified_list = []
    legal_list = KeyDataFrame['legalsource'].dropna().unique().tolist()
    illegal_list = KeyDataFrame['illegalsource'].dropna().unique().tolist()
    for i in range(len(VerifiDataFrame)):
        source_value = VerifiDataFrame.loc[i, 'source']
        file = VerifiDataFrame.loc[i, 'filename']
        result = gemini_checks_source(source_value,legal_list,illegal_list)
        print(result)
        if result == 0:
            """The File is legal hence Ignored"""
            print(f"[CLASS-D>>>DETECTING]: The file {file} is from LEGAL source. Hence Ignored...")
            wait()
        if result == 1:
            """The file is illegal hence proceeding"""
            print(f"[CLASS-D>>>DETECTING]: The file {file} is from ILLEGAL source. Proceeding to check key...")
            wait()
            filepath = os.path.abspath(os.path.join(os.getcwd(), "Internet", source_value, file))
            key = key_extractor(filepath)
            keyidentifier = KeyDataFrame['keyidentifier'].dropna().tolist()
            result2 = gemini_checks_key(key,keyidentifier)
            print("pirated!!!")
            if result2 == 0:
                """The file is ignored as it is not ours"""
                print(f"[CLASS-D>>>DETECTING]: The file {file} has unrecognized/missing KEY IDENTIFIER. Ignoring...")
                wait()
            if result2 == 1:
                print(f"[CLASS-D>>>DETECTING]: The file {file} contains KEY IDENTIFIER. Flagging for Admin!!!")
                wait()
                filename_flag.append(file)
                source_flag.append(source_value)
        if result == 2:
            unclassified_list.append(source_value)
    Detected_DataFrame = pd.DataFrame({'flagged_files': filename_flag,'file_source': source_flag})
    Detected_DataFrame.to_csv(detection_database_path, index=False)
    Unclassified_DataFrame = pd.DataFrame({'Unclassified': unclassified_list})
    Unclassified_DataFrame.to_csv(unclassified_database_path, index = False)
veri_loader = VerifiDataLoader()
VerifiDataFrame = veri_loader.load_data()
key_loader = KeyDataLoader()
KeyDataFrame = key_loader.load_data()


""" if VerifiDataFrame is not None:
    print(VerifiDataFrame)

if VerifiDataFrame is not None:
    results = read_raw_txts(VerifiDataFrame)
    for item in results[:3]:
        print("\n---")
        print(f"File: {item['filename']} from {item['source']}")
        print("Content Preview:")
        print(item['content'])
"""
# prompt1 = (f"""Given the website name (source): "{source}", determine its legality based on the following lists: Legal sources: {legal_list} Illegal sources: {illegal_list}, Return 0 if the source is clearly in the legal category, 1 if the source is clearly illegal, 2 if it's unclassified (not in either list or unclear).""")


Detection()
time.sleep(40)
