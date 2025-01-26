import json
from openai import OpenAI
import os
import requests
from prompts import system_prompt
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.environ["AIPROXY_TOKEN"])
client.base_url = "https://aiproxy.sanand.workers.dev/openai/"
BASE_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['AIPROXY_TOKEN']}",
}


def cosine_sim(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]
def request_ai_proxy(payload, debug=False, embedding=False):
    if embedding:
        print("USING EMBEDDINGS")
        BASE_URL = "http://aiproxy.sanand.workers.dev/openai/v1/embeddings"
    else:
        BASE_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    BASE_URL_DEBUG = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ["AIPROXY_TOKEN"]}"
        }
    # if debug == True:
    response = requests.post(BASE_URL, headers=headers, json=payload)
    # else:
    #     response = requests.post(BASE_URL_DEBUG, json=payload)

    if response.status_code == 200:
        result = response.json()
        # if debug == True:
        #     print("USING OLLAMA")
        #     return result["choices"][0]["message"]
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

    response = json.loads(requests.post(url=BASE_URL, headers=headers, json=data).text)
    answer = response["choices"][0]["message"]["content"]
    answer = json.loads(answer)
    func_name = answer["func_name"]
    args = answer["arguments"]
    if args:
        answer_json = {"func_name": func_name, "arguments": args}
    else:
        answer_json = {"func_name": func_name}
    return answer_json


# query = """
# format the data in the /data/format.md file
# """
# ans = execute_task(query)
# print(ans)
