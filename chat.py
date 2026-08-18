from llm import chat_completion

CHAT_SYSTEM_PROMPT = """You are a helpful assistant running inside a Telegram bot called Idea Executer.

Your capabilities:
- Answer questions and chat normally.
- Tell the user that if they send a YouTube/web link, a voice note, an audio file, or a video file, you will transcribe it, classify it into a content branch (app-idea, motivation, learning, business-strategy, creative, etc.), generate an action plan, and save it to Google Sheets and Google Drive.

Keep answers concise and useful."""


def chat_reply(message: str, history: list = None) -> str:
    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})
    return chat_completion(messages, temperature=0.7, max_tokens=1024)