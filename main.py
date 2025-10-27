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


############################################################################
# from utils.prompt_templates import GENERATION_PROMPT, REFINEMENT_PROMPT

# def main():
#     print("✅ Project initialized successfully!")

#     # Example problem for testing
#     problem = "Write a Python function that checks if a number is prime."
#     requirements = "Use a simple algorithm and handle edge cases."

#     # Fill the generation prompt
#     prompt = GENERATION_PROMPT.format(problem_description=problem, requirements=requirements)
#     print("\n--- Generated Prompt ---\n")
#     print(prompt)

#     # Example refinement
#     feedback = "The code fails for n=1 and even numbers."
#     existing_code = "def solve(n): return all(n % i != 0 for i in range(2, n))"
#     refine_prompt = REFINEMENT_PROMPT.format(existing_code=existing_code, feedback=feedback)
#     print("\n--- Refinement Prompt ---\n")
#     print(refine_prompt)

# if __name__ == "__main__":
#     main()


############################

# from agents.generator import GeneratorAgent

# def main():
#     print("✅ Project initialized successfully!")

#     # Initialize the Groq-based Generator Agent
#     generator = GeneratorAgent(api_key="GROQ_API_KEY_REDACTED")

#     problem = "Write a Python function that checks if a number is prime."
#     requirements = "Use a simple algorithm and handle edge cases."

#     generated_code = generator.generate_code(problem, requirements)

#     print("\n--- Generated Code ---\n")
#     print(generated_code)

# if __name__ == "__main__":
#     main()
####################################################
# main.py
from dotenv import load_dotenv
load_dotenv()
from agents.generator import GeneratorAgent
from agents.evaluator import EvaluatorAgent
from agents.critic import CriticAgent
from agents.refiner import RefinerAgent
from utils.logger import save_iteration_log

MAX_ITERATIONS = 3  # stop if not perfect after 3 tries


def main():
    print("✅ Project initialized successfully!")

    # Initialize all agents
    generator = GeneratorAgent(api_key="GROQ_API_KEY_REDACTED")
    evaluator = EvaluatorAgent()
    critic = CriticAgent(api_key="GROQ_API_KEY_REDACTED")
    refiner = RefinerAgent(api_key="GROQ_API_KEY_REDACTED")

    # Define problem and test cases
    problem = "Write a Python function that checks if a number is prime."
    requirements = "Use a simple algorithm and handle edge cases."
    test_cases = [(2, True), (3, True), (4, False), (17, True), (25, False), (1, False), (0, False)]

    # Step 1 — Generate initial code
    generated_code = generator.generate_code(problem, requirements)
    print("\n--- Initial Generated Code ---\n")
    print(generated_code)

    current_code = generated_code

    # Iterative loop for self-evolution
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n================ Iteration {iteration} ================\n")

        # Step 2 — Evaluate the code in sandbox
        eval_result = evaluator.evaluate_code(current_code)
        evaluator.pretty_print_result(eval_result)

        validation_result = None
        feedback = None

        # Step 3 — If basic sandbox execution is OK, run pytest
        if eval_result.get("success", False):
            print("🎉 Code executed successfully. Checking detailed test validation...")
            validation_result = refiner.validate_refinement(current_code, test_cases)

            if validation_result.get("success"):
                print("\n✅ All tests passed successfully!")

                # Save this successful iteration
                save_iteration_log(iteration, {
                    "status": "success",
                    "generated_code": current_code,
                    "evaluation_result": eval_result,
                    "critic_feedback": feedback,
                    "refined_code": current_code,
                    "pytest_result": validation_result
                })
                break
            else:
                print("\n❌ Some tests failed — triggering refinement loop.")
        else:
            print("\n⚠️ Execution failed — triggering refinement loop.")

        # Step 4 — Critic feedback
        feedback = critic.generate_feedback(current_code, eval_result)
        print("\n--- Critic Feedback ---\n")
        print(feedback)

        # Step 5 — Refine the code based on feedback
        current_code = refiner.refine_code(current_code, feedback)
        print("\n--- Refined Code ---\n")
        print(current_code)

        # 🧾 Step 6 — Log iteration data
        save_iteration_log(iteration, {
            "status": "incomplete",
            "generated_code": generated_code if iteration == 1 else None,
            "current_code": current_code,
            "evaluation_result": eval_result,
            "critic_feedback": feedback,
            "pytest_result": validation_result
        })

    else:
        print("\n🚫 Maximum iterations reached. Code still not fully correct.")
        # Save final iteration data for debugging
        save_iteration_log(MAX_ITERATIONS, {
            "status": "failed_after_max_iterations",
            "final_code": current_code,
            "evaluation_result": eval_result,
            "critic_feedback": feedback,
            "pytest_result": validation_result
        })


if __name__ == "__main__":
    main()



