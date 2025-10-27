# utils/logger.py
"""
Logger utility — saves iteration data (code, feedback, results) as JSON files.
"""

import os
import json
from datetime import datetime


def save_iteration_log(iteration: int, data: dict, results_dir: str = "results"):
    """
    Saves the given iteration data into a structured JSON file.
    """
    os.makedirs(results_dir, exist_ok=True)

    # Add timestamp and iteration info
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["iteration"] = iteration

    # Define output file path
    filename = os.path.join(results_dir, f"iteration_{iteration}.json")

    # Write JSON with pretty formatting
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"💾 Iteration {iteration} data saved to: {filename}")
