import json
from openai import OpenAI
import os
import requests
from prompts import system_prompt
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['AIPROXY_TOKEN']}",
}


def cosine_sim(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]


def request_ai_proxy(payload, debug=False, embedding=False):
    print("REQUESTING AI PROXY...")
    if embedding:
        print("USING EMBEDDINGS")
        BASE_URL = "http://aiproxy.sanand.workers.dev/openai/v1/embeddings"
    else:
        BASE_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    BASE_URL_DEBUG = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['AIPROXY_TOKEN']}",
    }
    if debug == False:
        response = requests.post(BASE_URL, headers=headers, json=payload)
    else:
        response = requests.post(BASE_URL_DEBUG, json=payload)

    if response.status_code == 200:
        result = response.json()
        if debug == True:
            print("USING OLLAMA")
            # For Ollama, directly return the response text
            if isinstance(result, dict) and 'response' in result:
                return result['response']
            return result
        print("USING OPENAI")
        if embedding:
            return result
        return result["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return 500


def get_func_name(task_descr: str):
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_descr},
        ],
    }

    response = json.loads(requests.post(
        url=BASE_URL, headers=headers, json=data).text)
    answer = response["choices"][0]["message"]["content"]
    answer = json.loads(answer)
    func_name = answer["func_name"]
    args = answer["arguments"]
    if args:
        answer_json = {"func_name": func_name, "arguments": args}
    else:
        answer_json = {"func_name": func_name}
    return answer_json


def code_generation_loop_back_cot(task_descr: str):
    # Initialize variables to track the conversation and code state
    conversation_history = []
    max_iterations = 5
    iteration = 0

    # Initial system prompt for code generation
    system_message = {
        "role": "system",
        "content": """You are an AI coding assistant that writes and debugs Python code. 
When given a task:
1. Write code to accomplish it
2. Test the code for errors
3. If there are errors, analyze them and suggest fixes
4. Continue this process until the code works correctly
Be precise and focus on writing working code.

An example task is : Scrape the following website : https://webscraper.io/test-sites/e-commerce/allinone and print the product names along with their prices.

"""
    }

    conversation_history.append(system_message)

    # Add the user's task description to the conversation
    user_message = {
        "role": "user",
        "content": task_descr
    }
    conversation_history.append(user_message)

    while iteration < max_iterations:
        # Get code generation/debugging response
        response = request_ai_proxy(
            payload={
                "model": "smallthinker:latest",
                "messages": conversation_history
            },
            debug=True
        )

        if not response:
            return "Error getting AI response"

        # Extract code from response
        try:
            # Execute the generated code in a safe environment
            code_output = {}
            exec_globals = {}
            try:
                print("CODE GENERATED: \n", response)
                print("\nEXECUTE CODE? y/n")
                if input() == "n":
                    return "Code execution skipped"
                exec(response, exec_globals)
                code_output["result"] = "Success"
                code_output["output"] = exec_globals.get(
                    "output", "Code executed successfully")
                return code_output
            except Exception as e:
                # If there are errors, add them to conversation for debugging
                error_message = {
                    "role": "user",
                    "content": f"""The code generated had the following error:
Error type: {type(e).__name__}
Error message: {str(e)}
Please debug the code and provide a corrected version."""
                }
                conversation_history.append(error_message)

                print("CONVERSATION HISTORY:", conversation_history)
        except Exception as parse_error:
            conversation_history.append({
                "role": "user",
                "content": f"Failed to parse response. Error: {str(parse_error)}"
            })

        iteration += 1

    return "Max iterations reached without successful code execution"

# code_generation_loop_back_cot("Clone the git repo : https://github.com/painful-bug/testing.git and make a commit to it")
