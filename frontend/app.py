import os
import json
from flask import Flask, send_from_directory, jsonify, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import your actual agents and utilities
from agents.generator import GeneratorAgent
from agents.evaluator import EvaluatorAgent
from agents.critic import CriticAgent
from agents.refiner import RefinerAgent
# Note: You need to ensure utils.logger.save_iteration_log is available in this file's context
# For simplicity, we'll redefine a stub if it's not needed by the Flask route return
def save_iteration_log(iteration, data):
    # This is a stub to prevent errors if the original logger is complex or unavailable
    # The actual logging to /results is done in your main.py if you run it directly
    print(f"DEBUG: Logging data for iteration {iteration}")


app = Flask(__name__)

# --- AGENT INITIALIZATION ---
# Initialize agents globally once on server start
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "GROQ_API_KEY_REDACTED")

try:
    generator = GeneratorAgent(api_key=GROQ_API_KEY)
    evaluator = EvaluatorAgent()
    critic = CriticAgent(api_key=GROQ_API_KEY)
    refiner = RefinerAgent(api_key=GROQ_API_KEY)
    
    # Define test cases (from your original main.py)
    TEST_CASES = [(2, True), (3, True), (4, False), (17, True), (25, False), (1, False), (0, False)]
    MAX_ITERATIONS = 3
    print("✅ All agents initialized and ready for web requests.")
except Exception as e:
    print(f"⚠️ Agent initialization failed. Check API keys and agent constructors: {e}")
    # Exit or handle error appropriately in production

# --- WEB ROUTES ---

@app.route('/')
def serve_index():
    """Serves the main HTML dashboard file."""
    return send_from_directory('.', 'index.html')


@app.route('/api/run_agent', methods=['POST'])
def run_agent_workflow():
    """
    Executes the full iterative agent cycle based on the frontend input.
    """
    
    data = request.json
    problem = data.get('problem', 'Write a Python function.')
    requirements = data.get('requirements', 'Standard requirements.')

    # List to store the results of each step for the frontend visualization
    workflow_steps = []
    current_code = ""
    
    try:
        # Step 1: Initial Generation
        generated_code = generator.generate_code(problem, requirements)
        current_code = evaluator.clean_code(generated_code) # Clean immediately after generation
        
        workflow_steps.append({
            "agent": "Generator", "step": "Initial Generation", "delay": 2000, 
            "success": True, "code": current_code,
            "log": "Initial code generated. Ready for evaluation.", "status": "Evaluation Required"
        })
        
        # Iterative Loop
        for iteration in range(1, MAX_ITERATIONS + 1):
            
            # Step 2: Evaluate the code in sandbox
            eval_result = evaluator.evaluate_code(current_code)
            is_successful = eval_result.get("success", False)
            
            workflow_steps.append({
                "agent": "Evaluator", "step": f"Sandbox Test (Iter {iteration})", "delay": 1500, 
                "success": is_successful, "code": None,
                "log": f"Sandbox Result: {'Success' if is_successful else 'Failure'}. Output/Error: {eval_result.get('error', eval_result.get('output', ''))[:100]}...", 
                "status": "Sandbox OK" if is_successful else "Execution Error"
            })

            validation_result = None
            feedback = None

            # Step 3: Check for Final Success (only if sandbox passed)
            if is_successful:
                # Run the deeper validation with unit tests
                validation_result = refiner.validate_refinement(current_code, TEST_CASES)
                all_tests_passed = validation_result.get("success")

                workflow_steps.append({
                    "agent": "Evaluator", "step": f"Pytest Validation (Iter {iteration})", "delay": 1000, 
                    "success": all_tests_passed, "code": None,
                    "log": validation_result.get('details', 'No details provided.'),
                    "status": "Tests Passed" if all_tests_passed else "Tests Failed"
                })

                if all_tests_passed:
                    # Final Success - Break the loop
                    break 

            # If not fully successful (or loop continues): Critic and Refiner steps
            if iteration < MAX_ITERATIONS and not all_tests_passed: 
                
                # Step 4: Critic feedback
                feedback = critic.generate_feedback(current_code, eval_result)
                
                workflow_steps.append({
                    "agent": "Critic", "step": f"Feedback Generation (Iter {iteration})", "delay": 1000, 
                    "success": False, "code": None,
                    "log": f"CRITIQUE: {feedback[:200]}...", 
                    "status": "Refinement Required"
                })
                
                # Step 5: Refine the code
                refined_code = refiner.refine_code(current_code, feedback)
                current_code = refined_code
                
                workflow_steps.append({
                    "agent": "Refiner", "step": f"Code Refinement (Iter {iteration})", "delay": 2500, 
                    "success": True, "code": current_code,
                    "log": "Refinement applied. Running next iteration.", 
                    "status": "Refined & Ready"
                })
            elif iteration == MAX_ITERATIONS:
                # Max iterations reached without success
                workflow_steps.append({
                    "agent": "System", "step": "Cycle Complete", "delay": 500, 
                    "success": False, "code": None,
                    "log": "Maximum iterations reached. Final code may contain errors.", 
                    "status": "Cycle Finished (Incomplete)"
                })
        
        return jsonify({"success": True, "workflow": workflow_steps})
        
    except Exception as e:
        # Catch any critical error during the entire process
        error_message = f"FATAL ERROR during agent execution: {str(e)}"
        print(error_message)
        workflow_steps.append({
             "agent": "Error", "step": "Critical Failure", "delay": 100, 
            "success": False, "code": None,
            "log": error_message, 
            "status": "FATAL ERROR"
        })
        return jsonify({"success": False, "error": error_message, "workflow": workflow_steps})


if __name__ == '__main__':
    # You must install Flask first: pip install Flask
    app.run(debug=True)