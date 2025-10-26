# sandbox/runner.py
"""
This file runs inside Docker to execute user-generated code safely.
"""

import os
import subprocess
import json
import sys
import time

def run_code():
    code_path = os.environ.get("CODE_PATH", "candidate.py")
    start_time = time.time()

    try:
        result = subprocess.run(
            ["python", code_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
            "success": result.returncode == 0,
            "runtime": round(time.time() - start_time, 2)
        }
    except subprocess.TimeoutExpired:
        output = {"stdout": "", "stderr": "⏰ Execution timed out!", "success": False}
    print(json.dumps(output))

if __name__ == "__main__":
    run_code()
