# agents/refiner.py
from groq import Groq
from utils.prompt_templates import REFINEMENT_PROMPT
from tests.test_runner import run_pytest_on_code
import os, json, re


class RefinerAgent:
    def __init__(self, api_key=None, model_name="llama-3.1-8b-instant"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("⚠️ GROQ_API_KEY not found.")
        self.model_name = model_name
        self.client = Groq(api_key=self.api_key)
        print(f"🔁 Refiner Agent initialized with Groq model: {self.model_name}")

    def _clean_code(self, code: str) -> str:
        """Cleans the LLM-generated code to remove markdown and explanations."""
        # Extract fenced code if present
        blocks = re.findall(r"```(?:python)?\s*([\s\S]*?)```", code, flags=re.IGNORECASE)
        if blocks:
            code = max(blocks, key=len)
        # Remove extra text lines like "Here's the code..."
        code = re.sub(r"^(Here[’']?s|Below|The code).*", "", code.strip(), flags=re.IGNORECASE | re.MULTILINE)
        code = re.sub(r"```+", "", code)
        return code.strip()

    def refine_code(self, existing_code: str, feedback: str):
        """Uses the LLM to fix the code based on critic feedback."""
        prompt = REFINEMENT_PROMPT.format(existing_code=existing_code, feedback=feedback)
        print("🧩 Sending refinement prompt to Groq...")

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a Python code refiner that improves existing code only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=800
        )

        refined_code = response.choices[0].message.content.strip()
        cleaned_code = self._clean_code(refined_code)
        return cleaned_code

    def validate_refinement(self, refined_code: str, test_cases: list):
        """Runs pytest-based validation for the refined code."""
        print("🧪 Running pytest validation...")
        result = run_pytest_on_code(refined_code, test_cases)
        print("✅ Pytest execution completed.")
        return result
