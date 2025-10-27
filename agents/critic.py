# agents/critic.py
"""
Critic Agent — analyzes evaluator results and provides feedback
for refining or validating generated code.
"""

from groq import Groq
from utils.prompt_templates import CRITIC_PROMPT
import os, json


class CriticAgent:
    def __init__(self, api_key: str = None, model_name: str = "llama-3.1-8b-instant"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("⚠️ GROQ_API_KEY not found. Set it as an environment variable or pass it directly.")
        self.model_name = model_name
        self.client = Groq(api_key=self.api_key)
        print(f"🧠 Critic Agent initialized with Groq model: {self.model_name}")

    def generate_feedback(self, candidate_code: str, eval_result: dict) -> str:
        """
        Generate feedback based on code and evaluator output.
        """
        test_output = json.dumps(eval_result, indent=4)
        prompt = CRITIC_PROMPT.format(candidate_code=candidate_code, test_output=test_output)

        print("🧩 Sending code and test output to Groq Critic Agent...")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a code review AI that provides constructive feedback on Python code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=400
        )

        feedback = response.choices[0].message.content.strip()
        return feedback
