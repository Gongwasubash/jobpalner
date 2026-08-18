import requests

from config import GROQ_API_KEY, WHISPER_MODEL

GROQ_TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


def transcribe_audio(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        response = requests.post(
            GROQ_TRANSCRIBE_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            files={"file": (audio_path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1], f, "audio/mpeg")},
            data={
                "model": WHISPER_MODEL,
                "response_format": "text",
                "temperature": "0",
            },
            timeout=300,
        )
    response.raise_for_status()
    return response.text.strip()