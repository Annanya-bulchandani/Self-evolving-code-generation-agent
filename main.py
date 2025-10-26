# from utils.sandbox_runner import run_code_in_sandbox

# def main():
#     print("✅ Project initialized successfully!")

#     # Test the sandbox integration
#     test_code = "print('Hello from integrated Docker sandbox!')"
#     result = run_code_in_sandbox(test_code)

#     print("\n--- Sandbox Integration Test ---")
#     print(result)

# if __name__ == "__main__":
#     main()

from utils.prompt_templates import GENERATION_PROMPT, REFINEMENT_PROMPT

def main():
    print("✅ Project initialized successfully!")

    # Example problem for testing
    problem = "Write a Python function that checks if a number is prime."
    requirements = "Use a simple algorithm and handle edge cases."

    # Fill the generation prompt
    prompt = GENERATION_PROMPT.format(problem_description=problem, requirements=requirements)
    print("\n--- Generated Prompt ---\n")
    print(prompt)

    # Example refinement
    feedback = "The code fails for n=1 and even numbers."
    existing_code = "def solve(n): return all(n % i != 0 for i in range(2, n))"
    refine_prompt = REFINEMENT_PROMPT.format(existing_code=existing_code, feedback=feedback)
    print("\n--- Refinement Prompt ---\n")
    print(refine_prompt)

if __name__ == "__main__":
    main()
