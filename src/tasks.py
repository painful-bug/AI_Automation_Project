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
import duckdb
# import whisper
from bs4 import BeautifulSoup
from PIL import Image
import markdown
import csv
import speech_recognition as sr
from pydub import AudioSegment
import subprocess
import sys

load_dotenv()


# Task 1
def generate_data_files(user_email: str):
    subprocess.Popen(
        [
            "uv",
            "run",
            "https://raw.githubusercontent.com/ANdIeCOOl/TDS-Project1-Ollama_FastAPI-/refs/heads/main/datagen.py",
            f"{user_email}",
            "--root",
            "./data",
        ]
    )
    print("data generated successfully")


# Task 2
def format_markdown_file(path="./data/format.md"):
    subprocess.Popen(
        ["prettier", "./data/format.md", "--write", "--parser", "markdown"],
    )
    print("data formatted successfully")


# Task 3
def count_wednesdays_in_dates():
    count = 0
    date_formats = [
        "%Y/%m/%d %H:%M:%S",  # 2017/01/31 23:59:59
        "%Y-%m-%d",  # 2017-01-31
        "%d-%b-%Y",  # 31-Jan-2017
        "%b %d, %Y",  # Jan-31-2017
    ]
    with open("./data/dates.txt") as f:
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
    with open("./data/dates-wednesdays.txt", "w") as f:
        f.write(str(count))


# Task 4
def sort_contacts():
    with open("./data/contacts.json", "r") as f:
        contacts = json.load(f)
        sorted_contacts = sorted(
            contacts, key=lambda x: (x["last_name"], x["first_name"])
        )
    with open("./data/contacts-sorted.json", "w") as f:
        json.dump(sorted_contacts, f)


# Task 5
def extract_recent_log_lines():
    dir_path = "./data/logs/"
    log_files = os.listdir(dir_path)
    max_filename = max(log_files, key=lambda x: int(x.split("-")[1].split(".")[0]))
    with open(f"./data/logs/{max_filename}", "r") as f:
        lines = [next(f) for _ in range(10)]
        with open("./data/logs-recent.txt", "w") as fw:
            for line in lines:
                fw.write(line)


# Task 6
def create_docs_index():
    index = {}
    p = pathlib.Path("./data/docs")
    for i in p.rglob("*"):
        if i.is_file() and i.suffix == ".md":
            with open(i, "r") as f:
                title = f.readline().strip("#").strip()
                index[i.name] = title
    with open("./data/index.json", "w") as f:
        json.dump(index, f)


# Task 7
def extract_sender_email():
    with open("./data/email.txt", "r") as f:
        email_file_contents = f.read()
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": f"Extract the sender's email address from the following text : {email_file_contents} and return only the sender's email address, nothing else",
            }
        ],
    }
    response: Json = request_ai_proxy(payload, debug=True)
    print("RESPONSE : ", response)
    with open("./data/email-sender.txt", "w") as f:
        f.write(response)


# Task 8 - PENDING
def extract_credit_card_number():
    image_path = "./data/credit_card.png"

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a specialized OCR assistant. Your only task is to analyze the provided image and return ONLY the 16-digit credit card number, with no additional text, commentary, or formatting. Do not offer any other information or make any assumptions about the card's validity.Format your response as exactly 16 digits with no spaces or separators. Nothing else should be included in your response",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    }
                ],
            },
        ],
    }

    cno = request_ai_proxy(payload=payload)
    with open("./data/credit-card.txt", "w") as f:
        f.write(cno)
    f.close()


# Task 9
def find_most_similar_comments():
    comments = []
    with open("./data/comments.txt", "r") as f:
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
    with open("./data/comments-similar.txt", "w") as f:
        f.write(comments[i] + "\n")
        f.write(comments[j] + "\n")


# Task 10
def calculate_gold_ticket_sales():
    conn = sqlite3.connect("./data/ticket-sales.db")
    cur = conn.cursor()
    total_sales = cur.execute(
        "SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"
    ).fetchone()[0]
    print("Total sales of Gold tickets : ", total_sales)
    conn.close()


# Task B3 - Fetch data from an API and save it

def fetch_api_data(url=None):
    if not url:
        url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url)
    data = response.json()
    with open("./data/api_data.json", "w") as f:
        json.dump(data, f)

# Task B4 -  Clone a git repo and make a commit

def clone_and_commit(url=None):
    if not url:
        url = "https://github.com/painful-bug/testing.git"
    repo_name = url.split('/')[-1].split('.')[0]
    subprocess.Popen(["git", "clone", url, f"./data/{repo_name}"])
    subprocess.Popen(["touch", f"./data/{repo_name}/commit.txt"])
    subprocess.Popen(["echo", "This is a commit message", ">", f"./data/{repo_name}/commit.txt"])
    subprocess.Popen(["git", "add", "."], cwd=f"./data/{repo_name}")
    subprocess.Popen(["git", "commit", "-m", "b4 testing commit"], cwd=f"./data/{repo_name}")
    print("Repo cloned and commit made successfully")

# Task B5 - Run a SQL query on a SQLite or DuckDB database

def run_sql_query(query, db_type, db_path=None):
    print("DB_TYPE : ", db_type)
    print("DB_PATH : ", db_path)
    print("QUERY : ", query)
    print("Running SQL query...")
    if db_type == "sqlite":
        conn = sqlite3.connect(db_path or "./data/ticket-sales.db")
        cur = conn.cursor()
        resp = cur.execute(query).fetchall()
        print("QUERY RESPONSE : ", resp)
        conn.commit()
        conn.close()
    elif db_type == "duckdb":
        conn = duckdb.connect(db_path or "./data/ticket-sales.db")
        resp = conn.sql(query).fetchall()
        print("QUERY RESPONSE : ", resp)
        conn.close()
    else:
        print("Invalid database type")
    return resp
# Task B6 - Extract data from (i.e. scrape) a website
def scrape_website_data(url):
    output_file = "./data/website_data.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    with open(output_file, "w") as file:
        file.write(soup.prettify())
    return soup.prettify()

def compress_image(input_file, quality, output_file="../data/compressed_image.jpg"):
    img = Image.open(input_file)
    img.save(output_file, quality=quality)

def convert_markdown_to_html(input_file: str, output_file: str = "../data/markdown_to_html.html"):
    with open(input_file, "r") as file:
        html = markdown.markdown(file.read())
    with open(output_file, "w") as file:
        file.write(html)

def filter_csv_api_endpoint():
    return """
from flask import Flask

app = Flask()

def filter_csv(input_file: str, column: str, value: str, output_file: str):
    results = []
    with open(input_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[column] == value:
                results.append(row)
    with open(output_file, "w") as file:
        json.dump(results, file)

@app.route("/filter_csv", methods=["POST"])
def filter_csv():
    input_file = request.args.get("input_file")
    column = request.args.get("column")
    value = request.args.get("value")
    output_file = request.args.get("output_file")
    filter_csv(input_file, column, value, output_file)
    return {"result" : "ok"}, 200
"""      


def check_dependencies():
    # Check if ffmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Error: ffmpeg is not installed. Install it using:")
        print("sudo apt-get update && sudo apt-get install ffmpeg")
        sys.exit(1)

def transcriber(audio_path):
    check_dependencies()
    # Check if input file exists
    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' not found")
        return
    
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Convert mp3 to wav using pydub
    print("Converting mp3 to wav...")
    try:
        audio = AudioSegment.from_mp3(audio_path)
        wav_path = "/tmp/temp_audio.wav"  # Using /tmp directory for temporary files
        audio.export(wav_path, format="wav")
    except Exception as e:
        print(f"Error converting audio: {e}")
        return
    
    # Transcribe the audio
    print("Transcribing audio...")
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            
            # Save transcription to file
            output_path = os.path.join(os.getcwd(), "transcription.txt")
            with open(output_path, "w") as f:
                f.write(text)
            print(f"Transcription saved to: {output_path}")
            
        except sr.UnknownValueError:
            print("Speech recognition could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from speech recognition service; {e}")
        finally:
            # Clean up temporary wav file
            if os.path.exists(wav_path):
                os.remove(wav_path)

# def transcriber(file_path):
#     """
#     Given a path to an audio file, this function:
#     1. Detects the language of the audio.
#     2. Transcribes the audio in that detected language.
#     3. Saves the transcription to 'transcription.txt'.
#     """

#     if not os.path.exists(file_path):
#         print("File not found")
#         return None

#     try:
#         # Load the Whisper model (automatically detects language and transcribes accordingly)
#         model = whisper.load_model("base")

#         # Transcribe the audio file
#         result = model.transcribe(file_path)
#         transcription = result.get("text", "")
#         detected_language = result.get("language", "unknown")
#         print(f"Detected language: {detected_language}")

#         # Save the transcription in a file
#         with open("transcription.txt", "w", encoding="utf-8") as f:
#             f.write(transcription)

#         return transcription
#     except Exception as e:
#         print(f"An error occurred during transcription: {e}")
#         return None

# run_sql_query('')
