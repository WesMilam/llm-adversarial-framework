# Utils
import csv
import os
from datetime import datetime

def get_timestamp():
    """
    Returns current timestamp string for filenames and logging.
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def log_to_csv(filepath, headers, row):
    """
    Appends a row of results to a CSV file, creating it with headers if it doesn't exist.

    Args:
        filepath (str): Path to the CSV file.
        headers (list): List of column headers.
        row (list): List of values matching the header order.
    """
    file_exists = os.path.isfile(filepath)

    with open(filepath, mode="a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)
