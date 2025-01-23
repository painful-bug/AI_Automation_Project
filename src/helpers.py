import json
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
import requests
from requests.api import head

load_dotenv()

system_prompt = """
You are an AI Automation Agent. You will be given the description of a task to execute, and a list of functions you must call to complete the task. You have to understand what task is being asked of you, then look for a function among the given list of functions that can perform the given task, and return only it's name in json format : "{ "func_name" : "{name of the function}" }". Do not output anything else. The list of functions provided to you are as follows :
    ["generate_data_files","format_markdown_file","count_wednesdays_in_dates","sort_contacts","extract_recent_log_lines","create_docs_index","extract_sender_email","extract_credit_card_number","find_most_similar_comments","calculate_gold_ticket_sales"]


    A detailed example of the tasks and the corresponding functions is as follows :
        1. Install uv (if required) and run https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/datagen.py with ${user.email} as the only argument. Function to be called : generate_data_files
        2. Format the contents of /data/format.md using prettier, updating the file in-place. Function to be called : format_markdown_file
        3. The file /data/dates.txt contains a list of dates, one per line. Count the number of Wednesdays in the list, and write just the number to /data/dates-wednesdays.txt. Function to be called : count_wednesdays_in_dates
        4. Sort the array of contacts in /data/contacts.json by last_name, then first_name, and write the result to /data/contacts-sorted.json. Function to be called : sort_contacts
        5. Write the first line of the 10 most recent .log file in /data/logs/ to /data/logs-recent.txt, most recent first. Function to be called : extract_recent_log_lines
        6. Find all Markdown (.md) files in /data/docs/. For each file, extract the first header line (the first line starting with #). Create an index file /data/docs/index.json that maps each filename (without the path) to its title (e.g. {"README.md": "Home", "large-language-models.md": "Large Language Models", ...}). Function to be called : create_docs_index
        7. /data/email.txt contains an email message. Pass the content to an LLM with instructions to extract the sender's email address, and write just the email address to /data/email-sender.txt. Function to be called : extract_sender_email
        8. /data/credit-card.png contains a credit card number. Pass the image to an LLM, have it extract the card number, and write it without spaces to /data/credit-card.txt. Function to be called : extract_credit_card_number
        9. /data/comments.txt contains a list of comments, one per line. Using embeddings, find the most similar pair of comments and write them to /data/comments-similar.txt. Function to be called : find_most_similar_comments
        10. The SQLite database file /data/ticket-sales.db has a tickets with columns type, units, and price. Each row is a customer bid for a concert ticket. What is the total sales of all the items in the "Gold" ticket type? Write the number in /data/ticket-sales-gold.txt. Function to be called : calculate_gold_ticket_sales
"""
client = OpenAI(api_key=os.environ["AIPROXY_TOKEN"])
client.base_url = "https://aiproxy.sanand.workers.dev/openai/"
BASE_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['AIPROXY_TOKEN']}"
}


def execute_task(task_descr: str):
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": task_descr
            }
        ]
    }

    response = json.loads(requests.post(
        url=BASE_URL,
        headers=headers,
        json=data
    ).text)
    answer = response["choices"][0]['message']['content']
    answer = json.loads(answer)
    answer = answer["func_name"]
    return answer

query = """
pull comments from /data/comments.txt, and group comments which are similar in /data/comments-similar.txt
"""
ans = execute_task(query)
print(ans)