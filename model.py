import os

from dotenv import load_dotenv
from openai import OpenAI
from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    MODEL
)

load_dotenv()

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set")
if not OPENROUTER_BASE_URL:
    raise ValueError("OPENROUTER_BASE_URL is not set")
if not MODEL:   
    raise ValueError("MODEL is not set")
client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)

MODEL = MODEL


def chat(messages: list, tools: list | None = None):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto" if tools else None,
    )

    return response.choices[0].message


if __name__ == "__main__":
    messages = [
        {
            "role": "system",
            "content": "You are a helpful personal assistant.",
        },
        {
            "role": "user",
            "content": "How many r's are in the word 'strawberry'?",
        },
    ]

    response = chat(messages)

    print(response.content)