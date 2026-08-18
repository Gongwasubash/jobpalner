import requests

from config import CLASSIFIER_MODEL, GROQ_API_KEY

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

CHAT_SYSTEM_PROMPT = """You are a helpful assistant running inside a Telegram bot called Idea Executer.

Your capabilities:
- Answer questions and chat normally.
- Tell the user that if they send a YouTube/web link, a voice note, an audio file, or a video file, you will transcribe it, classify it into a content branch (app-idea, motivation, learning, business-strategy, creative, etc.), generate an action plan, and save it to Google Sheets.

Keep answers concise and useful."""


def chat_reply(message: str, history: list = None) -> str:
    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    response = requests.post(
        GROQ_CHAT_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": CLASSIFIER_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()