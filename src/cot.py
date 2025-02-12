from helpers import request_ai_proxy
import re
import json
import subprocess

def extract_code(text):
    match = re.search(r"``````", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()

# Run the generated code by saving to a temporary file and capturing errors/output
def run_code(code):
    with open("temp_code.py", "w") as f:
        f.write(code)
    try:
        result = subprocess.run(["python", "temp_code.py"],
                                capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return result.stderr, None
        return None, result.stdout
    except Exception as e:
        return str(e), None

# Single-task agent implementing a self-correcting chain-of-thought mechanism
def ai_agent_system(initial_instruction):
    chain_of_thought = initial_instruction
    attempt = 1
    while True:
        print(f"\nAttempt {attempt}: Generating code using the current prompt...")
        payload = {
            "model": "smallthinker:latest",
            "messages": [
                {"role": "system", "content": (
                    "You are an expert Python programmer. Your task is to generate Python code "
                    "based on the instructions below. After generating the code, test it locally. "
                    "If it runs successfully, simply output the result; if errors occur, include the error "
                    "message and propose debugging steps.\nInstructions:\n" + chain_of_thought
                )}
            ]
        }
        response = request_ai_proxy(payload, debug=True)
        if response == 500:
            print("Error in API call. Exiting.")
            break

        code = extract_code(response)
        print("Generated code:\n", code)
        error, output = run_code(code)
        if error:
            print("Error encountered during code execution:")
            print(error)
            chain_of_thought += (
                "\n\nThe previously generated code produced the following error when executed:\n"
                f"{error}\n"
                "Please revise the code to fix this error and ensure the desired functionality."
            )
        else:
            print("Code executed successfully. Output:")
            print(output)
            break

        attempt += 1

# Helper to extract subtasks from a response.
# Tries to parse JSON first; if that fails, it falls back to extracting a numbered list.
def extract_subtasks(text):
    try:
        data = json.loads(text)
        if "steps" in data and isinstance(data["steps"], list):
            return data["steps"]
    except Exception:
        pass
    tasks = []
    for line in text.splitlines():
        m = re.match(r"^\d+\.\s*(.*)", line)
        if m:
            tasks.append(m.group(1))
    return tasks

# Process a single subtask with the self-prompting mechanism
def process_subtask(task_description, step_index):
    chain_of_thought = task_description
    attempt = 1
    while True:
        print(f"\nStep {step_index} - Attempt {attempt}: Generating code for subtask:\n{task_description}")
        payload = {
            "model": "smallthinker:latest",
            "messages": [
                {"role": "system", "content": (
                    "You are an expert Python programmer. Your task is to generate Python code "
                    "to perform the following subtask:\n" + chain_of_thought
                )}
            ]
        }
        response = request_ai_proxy(payload)
        if response == 500:
            print("API error encountered. Exiting subtask.")
            return
        code = extract_code(response)
        print("Generated code:\n", code)
        error, output = run_code(code)
        if error:
            print("Error encountered during subtask code execution:")
            print(error)
            chain_of_thought += (
                "\n\nThe previously generated code produced the following error when executed:\n"
                f"{error}\n"
                "Please revise the code to fix the error and ensure it accomplishes the subtask."
            )
        else:
            print("Subtask executed successfully. Output:")
            print(output)
            break
        attempt += 1

# Multi-step agent that breaks down a high-level task into subtasks and processes them sequentially
def multi_step_agent_system(initial_instruction):
    print("Dividing high-level task into subtasks...")
    payload = {
        "model": "smallthinker:latest",
        "messages": [
            {"role": "system", "content": (
                "You are an expert problem solver. Divide the following high-level task into sequential, "
                "well-defined subtasks. Output the subtasks as a numbered list.\nTask:\n" + initial_instruction
            )}
        ]
    }
    response = request_ai_proxy(payload, debug=True)
    if response == 500:
        print("Error in API call while dividing task.")
        return
    print("Subtask breakdown response:\n", response)
    subtasks = extract_subtasks(response)
    if not subtasks:
        print("No subtasks were extracted. Exiting.")
        return
    print("\nExtracted subtasks:")
    for i, step in enumerate(subtasks, 1):
        print(f"{i}. {step}")

    # Process each subtask sequentially
    for i, subtask in enumerate(subtasks, 1):
        print(f"\nProcessing subtask {i}/{len(subtasks)}:")
        process_subtask(subtask, i)

if __name__ == "__main__":
    # Example usage for a single-step task:
    # single_step_prompt = (
    #     "Write a Python program that performs a basic arithmetic operation. "
    #     "For example, add two numbers and print the result."
    # )
    # ai_agent_system(single_step_prompt)

    # Example usage for a multi-step task:
    multi_step_prompt = (
        "Clone a Git repository from a URl : https://github.com/painful-bug/testing.git and then create a new commit with the message 'Initial commit'."
    )
    multi_step_agent_system(multi_step_prompt)
