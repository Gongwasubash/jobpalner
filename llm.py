import requests

from config import (
    CLASSIFIER_MODEL,
    GROQ_API_KEY,
    MISTRAL_API_KEY,
    MISTRAL_BASE_URL,
    MISTRAL_MODEL,
    QWEN_API_KEY,
    QWEN_BASE_URL,
    QWEN_MODEL_NAME,
)

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


def _endpoint():
    if MISTRAL_API_KEY:
        url = MISTRAL_BASE_URL.rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
        return url, headers, MISTRAL_MODEL, False
    if QWEN_BASE_URL:
        url = QWEN_BASE_URL.rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {QWEN_API_KEY}"}
        return url, headers, QWEN_MODEL_NAME, True
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    return GROQ_CHAT_URL, headers, CLASSIFIER_MODEL, False


def chat_completion(messages, temperature: float = 0.3, max_tokens: int = 4000) -> str:
    url, headers, model, is_qwen = _endpoint()
    headers = dict(headers)
    headers.setdefault("Content-Type", "application/json")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if is_qwen:
        payload["chat_template_kwargs"] = {"enable_thinking": False}

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()