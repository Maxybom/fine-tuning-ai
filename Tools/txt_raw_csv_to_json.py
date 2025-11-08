import json
import os
import subprocess
import sys

file_name = "unreal_engine_5" 
csv_path = f"Tools/{file_name}.csv"
txt_path = f"Tools/{file_name}.txt"
json_path = f"Tools/{file_name}.json"
output_path = f"Tools/Export_json/{file_name}_dataset.json"

# Ensure pandas is available
try:
    import pandas as pd
except ImportError:
    print("Installing pandas...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas==2.3.0"])
    import pandas as pd

# Final dataset container
hf_dataset = []

if os.path.exists(csv_path):
    print(f"File found: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            prompt = row.get("prompt") or f"{row.get('topic','')} {row.get('api','')} {row.get('question','')}".strip()
            completion = row.get("answer", "")
            if prompt and completion:
                hf_dataset.append({"prompt": prompt, "completion": completion})
    except Exception as e:
        print(f"Error reading CSV: {e}")
    goto_save = True

elif os.path.exists(txt_path):
    print(f"File found: {txt_path}")
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            if "::" in line:
                parts = line.strip().split("::", 1)
                prompt = parts[0].strip()
                completion = parts[1].strip()
                if prompt and completion:
                    hf_dataset.append({"prompt": prompt, "completion": completion})
    except Exception as e:
        print(f"Error reading TXT: {e}")
    goto_save = True

elif os.path.exists(json_path):
    print(f"File found: {json_path}")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            raw_json = json.load(f)
        if isinstance(raw_json, dict):
            raw_json = list(raw_json.values())
        for item in raw_json:
            prompt = item.get("prompt") or f"{item.get('topic','')} {item.get('api','')} {item.get('question','')}".strip()
            completion = item.get("answer", "")
            if prompt and completion:
                hf_dataset.append({"prompt": prompt, "completion": completion})
    except Exception as e:
        print(f"Error reading JSON: {e}")
    goto_save = True

else:
    print("No valid input file found.")
    goto_save = False

# Remove duplicates and save
if goto_save:
    unique_dataset = []
    seen = set()
    for entry in hf_dataset:
        key = (entry["prompt"], entry["completion"])
        if key not in seen:
            unique_dataset.append(entry)
            seen.add(key)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(unique_dataset, f, ensure_ascii=False, indent=2)
        print(f"Fine-tuning JSON saved to: {output_path}")
    except Exception as e:
        print(f"Error saving JSON: {e}")
