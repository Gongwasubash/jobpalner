import json
import re

import requests

from classifier_prompt import CLASSIFIER_SYSTEM_PROMPT
from config import CLASSIFIER_MODEL, GROQ_API_KEY

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", raw, re.DOTALL)
    if fence:
        raw = fence.group(1).strip()
    else:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            raw = raw[start : end + 1]
    return json.loads(raw)


def classify_and_plan(transcript: str) -> dict:
    response = requests.post(
        GROQ_CHAT_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": CLASSIFIER_MODEL,
            "messages": [
                {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": f"TRANSCRIPT:\n\n{transcript}"},
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
        },
        timeout=300,
    )
    response.raise_for_status()
    raw = response.json()["choices"][0]["message"]["content"]
    return _extract_json(raw)