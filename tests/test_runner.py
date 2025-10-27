# tests/test_runner.py
"""
Test Runner — executes pytest inside sandbox environment.
Used by the Refiner Agent to validate generated code.
"""

import subprocess
import json
import tempfile
import os


def run_pytest_on_code(code: str, test_cases: list):
    """
    Dynamically creates a test file with given test cases and runs pytest.
    Returns test results as a structured dictionary.
    """
    # Create temporary directory for code + test
    with tempfile.TemporaryDirectory() as tempdir:
        code_path = os.path.join(tempdir, "candidate.py")
        test_path = os.path.join(tempdir, "test_candidate.py")

        # Write candidate code
        with open(code_path, "w") as f:
            f.write(code)

        # Generate test code dynamically
        test_code = "import candidate\n\n"
        for i, (inp, expected) in enumerate(test_cases):
            test_code += f"def test_case_{i}():\n"
            test_code += f"assert candidate.solve({inp}) == {expected}\n\n"

        with open(test_path, "w") as f:
            f.write(test_code)

        # Run pytest
        result = subprocess.run(
            ["pytest", "-q", "--tb=short", "--disable-warnings", test_path],
            cwd=tempdir,
            capture_output=True,
            text=True,
        )

        success = result.returncode == 0
        return {
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
