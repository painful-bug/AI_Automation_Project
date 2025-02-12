import subprocess
import re
import os
from helpers import request_ai_proxy


class AIAgent:
    def __init__(self, debug=False):
        self.history = []
        self.debug = debug
        self.subtasks = []
        self.current_subtask = 0

    def generate_initial_prompt(self, task):
        return [
            {"role": "system", "content": f"""You are an AI programming assistant that follows this strict workflow:
1. Task Analysis - Break complex tasks into sequential subtasks
2. Code Generation - Write executable Python code for the current subtask
3. Error Correction - If errors occur, analyze and fix the code
4. Iterate - Repeat until all subtasks are completed

Current Task: {task}

First, list the subtasks in order. Then generate code ONLY for the first subtask.
Output format:
Subtasks:
1. [subtask 1]
2. [subtask 2]
...

Code:
```python
[code here]



NOTE : Always prefer to perform an action using subprocess module if possible. If not, then use other Python code.
Always return some code. Never return a blank/null response
```"""}
        ]

    def request_ai(self, messages):
        payload = {
            "messages": messages,
            "model": "gpt-4o-mini" if not self.debug else "codellama",
        }
        resp = request_ai_proxy(payload, debug=self.debug)

        if self.debug:
            # Handle Ollama response
            if isinstance(resp, dict):
                return resp.get('response', '')
        # Handle OpenAI response
        return resp

    def extract_code_from_response(self, response):
        code_match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
        print(
            f"Extracted code: {code_match.group(1).strip() if code_match else None}")
        resp = code_match.group(1).strip() if code_match else None
        # print(f"Extracted code: {resp}")
        return resp

    def execute_code(self, code):
        try:
            result = subprocess.run(['python3', '-c', code],
                                    capture_output=True,
                                    text=True,
                                    check=True)
            return {
                "success": True,
                "output": result.stdout,
                "error": None
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "output": None,
                "error": f"{e.stderr}\nExit code: {e.returncode}"
            }

    def handle_error(self, code, error):
        debug_prompt = {
            "role": "user",
            "content": f"""Code failed with error:
{error}

Original code:
```python
{code}

Please:

Analyze the error

Explain the fix

Provide corrected code

Output format:
Analysis: [analysis]
Fix: [explanation]
Code:
[corrected code]


NOTE : Always prefer to perform an action using bash commands if possible. If not, then use Python code.
```"""
        }
        self.history.append(debug_prompt)
        return self.request_ai(self.history)

    def process_subtasks(self, response):
        subtask_section = re.search(
            r'Subtasks:\n(.*?)\n\n', response, re.DOTALL)
        if subtask_section:
            subtasks = [line.strip() for line in subtask_section.group(
                1).split('\n') if line.strip()]
            self.subtasks = subtasks
            self.current_subtask = 0

    def run_task(self, task):
        self.history = self.generate_initial_prompt(task)
        response = self.request_ai(self.history)
        print(f"Initial response:\n{response}")

        self.process_subtasks(response)

        while self.current_subtask < len(self.subtasks):
            print(
                f"\nProcessing subtask {self.current_subtask+1}/{len(self.subtasks)}: {self.subtasks[self.current_subtask]}")

            code = self.extract_code_from_response(response)
            if not code:
                raise ValueError("No code found in AI response")

            execution_result = self.execute_code(code)

            if execution_result['success']:
                print(
                    f"Subtask {self.current_subtask+1} completed successfully!")
                print(f"Output: {execution_result['output']}")
                self.current_subtask += 1
                if self.current_subtask < len(self.subtasks):
                    next_subtask = self.subtasks[self.current_subtask]
                    new_prompt = {
                        "role": "user",
                        "content": f"Current task progress: Completed subtask {self.current_subtask}/{len(self.subtasks)}\n\nNext subtask: {next_subtask}\n\nGenerate code for this subtask:"
                    }
                    self.history.append(new_prompt)
                    response = self.request_ai(self.history)
            else:
                print(f"Error in subtask {self.current_subtask+1}:")
                print(execution_result['error'])
                debug_response = self.handle_error(
                    code, execution_result['error'])
                print("\nDebugging response:")
                print(debug_response)
                response = debug_response
                self.history.append(
                    {"role": "assistant", "content": debug_response})

        return "All tasks completed successfully!"


# Example usage
if __name__ == "__main__":
    agent = AIAgent(debug=False)  # Set debug=True for local Ollama

    # Complex multi-step task
    task = """Clone the repository https://github.com/painful-bug/testing.git, change directory into the repository,
then create a new file called 'output.txt' with current timestamp inside the repository (do not create it outside the repository), 
and commit it to the repository"""
    try:
        result = agent.run_task(task)
        print(result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
