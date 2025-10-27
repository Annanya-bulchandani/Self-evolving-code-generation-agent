# agents/generator.py
"""
Generator Agent — uses Groq API (LLaMA 3 model) for fast hosted code generation.
No local model downloads required.
"""

from utils.prompt_templates import GENERATION_PROMPT
from groq import Groq
import os


class GeneratorAgent:
    def __init__(self, api_key: str = None, model_name: str = "llama-3.1-8b-instant"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("⚠️ GROQ_API_KEY not found. Set it as an environment variable or pass it directly.")
        self.model_name = model_name
        self.client = Groq(api_key=self.api_key)
        print(f"🔧 Generator Agent initialized with Groq model: {self.model_name}")

    def generate_code(self, problem_description: str, requirements: str):
        """
        Generates Python code using Groq-hosted LLaMA 3.
        """
        prompt = GENERATION_PROMPT.format(
            problem_description=problem_description,
            requirements=requirements
        )

        print("🚀 Sending prompt to Groq LLM...")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful AI coding assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=600
        )

        generated = response.choices[0].message.content
        return generated.strip()
