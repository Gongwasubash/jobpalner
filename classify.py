import json
import re

from classifier_prompt import CLASSIFIER_SYSTEM_PROMPT
from llm import chat_completion


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
    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
        {"role": "user", "content": f"TRANSCRIPT:\n\n{transcript}"},
    ]
    raw = chat_completion(messages, temperature=0.3, max_tokens=4000)
    return _extract_json(raw)