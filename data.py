import os
import random

# Directory to scan
base_dir = os.path.expanduser("~/VODA-S/Internet")

# Key pool
key_identities = [
    "Gf83hT2Xb91z", "Qp7rLk92VwX3", "zY71fMbPq8Kr", "2jXR9WcFbL6q", "Hn4z73LcAvTp",
    "Jw92mBZxT1eP", "Cb39LvPr8yKq", "Xy84ZqvR1bTc", "kW19pAXzLf7Q", "T8xCqK5vRzM2",
    "dPqL7Ax93ZkV", "VtXq19PrmY5K", "pZR84wTcXmL1", "GxL9vM2rqYZ5", "bT71XqvZcPaR",
    "KrqPXZ91wL3y", "aYX4z7KvcMLq", "MxRp29BLcTqV", "LfZpXqV137bw", "qwTP93LxmZvK"
]

custom_suffix = " "

available_keys = key_identities.copy()
random.shuffle(available_keys)

def fill_or_insert_key(filepath, key):
    with open(filepath, 'r+', encoding='utf-8') as f:
        lines = f.readlines()
        key_inserted = False

        for i, line in enumerate(lines):
            if line.startswith("key_identity:"):
                # If line is empty after colon, insert key
                if line.strip() == "key_identity:":
                    lines[i] = f"key_identity: {key}{custom_suffix}\n"
                    key_inserted = True
                    break
                else:
                    print(f"[SKIP] Key already present in {filepath}")
                    return

        if not key_inserted:
            # Add key_identity line at the top
            lines.insert(0, f"key_identity: {key}{custom_suffix}\n")

        # Write modified content
        f.seek(0)
        f.writelines(lines)
        f.truncate()

        print(f"[ADD] Inserted key into {filepath}")

def assign_keys():
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".txt"):
                filepath = os.path.join(root, file)

                if not available_keys:
                    print("[STOP] Ran out of keys!")
                    return

                key = available_keys.pop()
                fill_or_insert_key(filepath, key)

if __name__ == "__main__":
    assign_keys()
