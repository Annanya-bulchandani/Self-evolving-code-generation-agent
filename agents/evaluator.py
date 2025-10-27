# agents/evaluator.py
"""
Evaluator Agent — executes generated code safely inside Docker sandbox
and collects results such as output, errors, and execution status.
"""

from utils.sandbox_runner import run_code_in_sandbox
import re, json


class EvaluatorAgent:
    def __init__(self):
        print("🧩 Evaluator Agent initialized and ready.")

    def _extract_fenced_code(self, text: str) -> str | None:
        """
        If markdown code fences exist, return the largest fenced block content.
        """
        # Matches ```python ... ``` OR ``` ... ```
        blocks = re.findall(r"```(?:python)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
        if not blocks:
            return None
        # Choose the largest block (most likely the actual code)
        return max(blocks, key=len).strip()

    def _heuristic_clean(self, text: str) -> str:
        """
        Fallback cleanup when no code fences are present.
        - Removes a leading 'python' line
        - Keeps from the first code-like token
        - Drops common trailing explanations like 'This code ...'
        """
        # Normalize newlines
        text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

        # Remove a lone language header if present
        text = re.sub(r"^\s*python\s*$", "", text, flags=re.IGNORECASE | re.MULTILINE).strip()

        # Start from first likely code anchor
        anchors = ["def ", "class ", "import ", "from ", "#!", "if __name__ =="]
        start_idx = min((text.find(a) for a in anchors if a in text), default=0)
        candidate = text[start_idx:].strip()

        # Remove any trailing explanation paragraphs (common LLM narration)
        lines = candidate.split("\n")
        cleaned_lines = []
        for ln in lines:
            # Stop if line looks like prose (very heuristic)
            if re.match(r"^\s*(This code|The code|It |In this|Explanation|Here, )", ln):
                break
            cleaned_lines.append(ln)

        # Also strip any accidental leftover backticks anywhere
        cleaned = "\n".join(l for l in cleaned_lines if not l.strip().startswith("```")).strip()
        return cleaned

    def clean_code(self, raw: str) -> str:
        """
        Unified cleaner:
        1) Try to extract fenced code.
        2) Else, use heuristics to keep only code and drop narration.
        """
        fenced = self._extract_fenced_code(raw)
        code = fenced if fenced is not None else self._heuristic_clean(raw)

        # Final polish: remove any lingering triple backticks & leading 'python'
        code = re.sub(r"```+", "", code).strip()
        code = re.sub(r"^\s*python\s*\n", "", code, flags=re.IGNORECASE)

        return code.strip()

    def evaluate_code(self, generated_code: str):
        """
        Executes the given Python code inside Docker sandbox.
        Returns structured result with output, errors, and success flag.
        """
        print("⚙️ Evaluating generated code in sandbox...")
        cleaned_code = self.clean_code(generated_code)
        result = run_code_in_sandbox(cleaned_code)
        print("✅ Sandbox execution completed.")
        return result

    def pretty_print_result(self, result: dict):
        """
        Nicely formats and prints the sandbox execution results.
        """
        print("\n--- Evaluation Result ---")
        print(json.dumps(result, indent=4))
