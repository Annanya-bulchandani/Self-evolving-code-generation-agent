# # tests/test_runner.py
# """
# Test Runner — executes pytest inside sandbox environment.
# Used by the Refiner Agent to validate generated code.
# """

# import subprocess
# import json
# import tempfile
# import os


# def run_pytest_on_code(code: str, test_cases: list):
#     """
#     Dynamically creates a test file with given test cases and runs pytest.
#     Returns test results as a structured dictionary.
#     """
#     # Create temporary directory for code + test
#     with tempfile.TemporaryDirectory() as tempdir:
#         code_path = os.path.join(tempdir, "candidate.py")
#         test_path = os.path.join(tempdir, "test_candidate.py")

#         # Write candidate code
#         with open(code_path, "w") as f:
#             f.write(code)

#         # Generate test code dynamically
#         test_code = "import candidate\n\n"
#         for i, (inp, expected) in enumerate(test_cases):
#             test_code += f"def test_case_{i}():\n"
#             test_code += f"assert candidate.solve({inp}) == {expected}\n\n"

#         with open(test_path, "w") as f:
#             f.write(test_code)

#         # Run pytest
#         result = subprocess.run(
#             ["pytest", "-q", "--tb=short", "--disable-warnings", test_path],
#             cwd=tempdir,
#             capture_output=True,
#             text=True,
#         )

#         success = result.returncode == 0
#         return {
#             "success": success,
#             "stdout": result.stdout,
#             "stderr": result.stderr,
#             "returncode": result.returncode,
#         }

"""
Test Runner — executes pytest inside a temp dir.
Builds a dynamic test file that:
- Calls is_prime_number() if present, else is_prime()
- Supports success cases (True/False) and exception cases (TypeError, etc.)
- Uses flexible message checking for exceptions (substring match)
"""

import subprocess
import tempfile
import os
import sys
from typing import List, Tuple, Any


def run_pytest_on_code(code: str, test_cases: list):
    """
    test_cases: list of tuples (inp, expected)
      - For boolean expectations: expected is True/False
      - For exception expectations: expected is an Exception class or the string name, e.g., TypeError or "TypeError"
    """
    with tempfile.TemporaryDirectory() as tempdir:
        code_path = os.path.join(tempdir, "candidate.py")
        test_path = os.path.join(tempdir, "test_candidate.py")

        # 1) Write candidate code
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)

        # 2) Build test file
        lines = []
        lines.append("import candidate, pytest\n")
        lines.append(
            """
def _pick_func():
    # Prefer more explicit name if present
    if hasattr(candidate, "is_prime_number"):
        return candidate.is_prime_number
    if hasattr(candidate, "is_prime"):
        return candidate.is_prime
    # As a fallback, allow a top-level solve(n) that RETURNS a bool (not prints)
    if hasattr(candidate, "solve"):
        return candidate.solve
    raise AssertionError("No suitable function found (is_prime_number / is_prime / solve).")
            """.strip()
        )
        lines.append("\n")

        def py_literal(x: Any) -> str:
            # Render Python literal safely for embedding
            if isinstance(x, str):
                return repr(x)
            if isinstance(x, type) and issubclass(x, Exception):
                return x.__name__
            return repr(x)

        for i, (inp, expected) in enumerate(test_cases):
            expected_is_exception = False
            except_name = None

            # Detect exception expectations: either an Exception class or its name
            if isinstance(expected, type) and issubclass(expected, Exception):
                expected_is_exception = True
                except_name = expected.__name__
            elif isinstance(expected, str) and expected.lower().endswith("error"):
                expected_is_exception = True
                except_name = expected

            if expected_is_exception:
                # Flexible message check: only require the word 'integer' to appear
                lines.append(
                    f"""
def test_case_{i}():
    func = _pick_func()
    with pytest.raises({except_name}) as e:
        func({py_literal(inp)})
    # Flexible assertion on message to avoid brittle exact-string comparison
    assert "integer" in str(e.value).lower()
                    """.strip()
                )
            else:
                lines.append(
                    f"""
def test_case_{i}():
    func = _pick_func()
    assert func({py_literal(inp)}) == {py_literal(expected)}
                    """.strip()
                )
            lines.append("\n")

        test_code = "\n".join(lines)

        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_code)

        # 3) Run pytest via the current Python, so it works on Windows/virtualenv
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--tb=short", "--disable-warnings", test_path],
            cwd=tempdir,
            capture_output=True,
            text=True,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
