from pydantic import Json
from helpers import request_ai_proxy, cosine_sim
import json
import sqlite3

def extract_credit_card_number():
    import requests
    import base64
    import os
    from dotenv import load_dotenv
    load_dotenv()



    BASE_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ["AIPROXY_TOKEN"]}"
    }

    image_path = "../data/credit_card.png"

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that provides detailed and accurate descriptions of images. Focus on describing the objects, colors, textures, the overall scene, and most importantly, the text and numbers in the image. Be concise but thorough."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are given an image containing a credit card number. Extract the credit card number from the image"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
    }


    response = requests.post(BASE_URL, headers=headers, json=payload)


    if response.status_code == 200:
        result = response.json()
        print("RESULT:", result)
        cno = result["choices"][0]["message"]["content"]
        print("CREDIT CARD NUMBER:", cno)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def test():
    import requests
    import os
    import base64
    from dotenv import load_dotenv
    load_dotenv()

    image_path = "../data/credit_card.png"# Replace with your image URL

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    payload = {
            "model": "gpt-4o-mini",# Use the GPT-4 Vision model
            "messages": [
                {
                    "role": "system",  # System prompt to guide the model's behavior
                    "content": "You are a helpful assistant that provides detailed and accurate descriptions of images. Focus on describing the objects, colors, textures, the overall scene, and most importantly, the text and numbers in the image. Be concise but thorough."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are given an image containing a credit card number. Extract the credit card number from the image"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
        }




    headers = {
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('AIPROXY_TOKEN', ''),
    }


    response = requests.post('http://aiproxy.sanand.workers.dev/openai/v1/chat/completions', headers=headers, json=payload)
    print(response.json())
