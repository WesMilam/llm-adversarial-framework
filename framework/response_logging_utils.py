import csv
import os
from datetime import datetime

RESULTS_FILE = "results/model_responses.csv"
os.makedirs("results", exist_ok=True)

def log_response(prompt, model, response, source="manual", metadata=None):
    row = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "prompt": prompt,
        "response": response,
        "source": source,
    }
    if metadata:
        row.update(metadata)

    file_exists = os.path.isfile(RESULTS_FILE)
    with open(RESULTS_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
