import subprocess
from datetime import datetime
import json
import pathlib
import requests
import os
import base64
import sqlite3
from dotenv import load_dotenv
from pydantic import Json
from helpers import cosine_sim, request_ai_proxy
load_dotenv()




# Task 1
def generate_data_files(user_email: str):
    subprocess.Popen(
        [
            "uv",
            "run",
            "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/datagen.py",
            f"{user_email}",
            "--root",
            "../data"
        ]
    )
    print("data generated successfully")

# Task 2
def format_markdown_file(path="../data/format.md"):

        subprocess.Popen(["prettier", "../data/format.md", "--write", "--parser", "markdown"],)
        print("data formatted successfully")

# Task 3
def count_wednesdays_in_dates():

    count = 0
    date_formats = [
        "%Y/%m/%d %H:%M:%S", # 2017/01/31 23:59:59
        "%Y-%m-%d", # 2017-01-31
        "%d-%b-%Y", # 31-Jan-2017
        "%b %d, %Y", # Jan-31-2017
    ]
    with open("../data/dates.txt") as f:
        for i in f:
            date = i.strip()
            if date:
                for format in date_formats:
                    try:
                        date_obj = datetime.strptime(date, format)
                        if date_obj.weekday() == 2:
                            count += 1
                    except ValueError:
                        continue
    with open("../data/dates-wednesdays.txt", "w") as f:
        f.write(str(count))

# Task 4
def sort_contacts():

    with open("../data/contacts.json", "r") as f:
        contacts = json.load(f)
        sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))
    with open("../data/contacts-sorted.json", "w") as f:
        json.dump(sorted_contacts, f)

# Task 5
def extract_recent_log_lines():
    dir_path = "../data/logs/"
    log_files = os.listdir(dir_path)
    max_filename = max(log_files, key=lambda x: int(x.split("-")[1].split(".")[0]))
    with open(f"../data/logs/{max_filename}", "r") as f:
        lines = [next(f) for _ in range(10)]
        with open("../data/logs-recent.txt", "w") as fw:
            for line in lines:
                fw.write(line)
# Task 6
def create_docs_index():
    index = {}
    p = pathlib.Path("../data/docs")
    for i in p.rglob("*"):
        if i.is_file() and i.suffix == ".md":
            with open(i, "r") as f:
                title = f.readline().strip("#").strip()
                index[i.name] = title
    with open("../data/index.json", "w") as f:
        json.dump(index, f)

# Task 7
def extract_sender_email():
    with open("../data/email.txt", "r") as f:
        email_file_contents = f.read()
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": f"Extract the sender's email address from the following text : {email_file_contents} and return only the sender's email address, nothing else"
            }
        ]
    }
    response: Json = request_ai_proxy(payload)
    print("RESPONSE : ", response)
    with open("../data/email-sender.txt", "w") as f:
        f.write(response)

# Task 8 - PENDING
def extract_credit_card_number():
    pass

# Task 9
def find_most_similar_comments():
    comments = []
    with open("../data/comments.txt", "r") as f:
        for i in f:
            comment = i.strip()
            comments.append(comment)
    payload = {
        "model": "text-embedding-3-small",
        "input": comments,
    }
    response: Json = request_ai_proxy(payload, embedding=True)
    embeddings_list = [i["embedding"] for i in response["data"]]

    similarities = []
    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            sim = cosine_sim(embeddings_list[i], embeddings_list[j])
            similarities.append(((i, j), sim))

    # Sort similarities in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Print the most similar lines
    print("Most similar comments:")
    (i, j), sim = similarities[0]
    print(f"Similarity: {sim:.4f}")
    print(f"Line {i + 1}: {comments[i]}")
    print(f"Line {j + 1}: {comments[j]}")
    print()
    with open("../data/comments-similar.txt", "w") as f:
        f.write(comments[i] + "\n")
        f.write(comments[j] + "\n")

# Task 10
def calculate_gold_ticket_sales():
    conn = sqlite3.connect("../data/ticket-sales.db")
    cur = conn.cursor()
    total_sales = cur.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'").fetchone()[0]
    print("Total sales of Gold tickets : ", total_sales)
    conn.close()
# generate_data_files("ujanaishik109@gmail.com")
