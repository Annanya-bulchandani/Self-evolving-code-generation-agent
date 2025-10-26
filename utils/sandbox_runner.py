# utils/sandbox_runner.py
"""
Runs Python code safely inside the Docker sandbox container.
Automatically mounts the code, executes it, and returns structured results.
"""

import subprocess
import tempfile
import os
import json
import shutil

def run_code_in_sandbox(code: str):
    """
    Executes Python code inside the Docker sandbox and returns a dict result.
    """
    temp_dir = tempfile.mkdtemp(prefix="sandbox_")
    code_path = os.path.join(temp_dir, "candidate.py")

    # Write code into a temporary file
    with open(code_path, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        # Build Docker command
        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--cpus", "0.5",
            "--memory", "256m",
            "-v", f"{temp_dir}:/sandboxuser:ro",
            "-e", f"CODE_PATH=/sandboxuser/candidate.py",
            "code-sandbox:latest"
        ]

        # Run command and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Try parsing JSON from container output
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            output = {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "success": result.returncode == 0
            }

        return output

    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "⏰ Docker execution timed out!", "success": False}

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
