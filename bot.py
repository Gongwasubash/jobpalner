import os
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

from config import ensure_config, TELEGRAM_BOT_TOKEN
from media import is_media_file
from pipeline import process

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

HEALTH_PORT = int(os.getenv("PORT", "8080"))
_last_update_id = 0


def start_health_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):
            pass

    server = HTTPServer(("0.0.0.0", HEALTH_PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Health server on port {HEALTH_PORT}")


def get_updates(timeout: int = 30):
    global _last_update_id
    try:
        r = requests.get(
            f"{TELEGRAM_API}/getUpdates",
            params={"offset": _last_update_id + 1, "timeout": timeout},
            timeout=timeout + 10,
        )
        r.raise_for_status()
        return r.json().get("result", [])
    except requests.RequestException as exc:
        print(f"getUpdates error: {exc}")
        return []


def get_file_path(file_id: str) -> str:
    info = requests.get(
        f"{TELEGRAM_API}/getFile",
        params={"file_id": file_id},
        timeout=30,
    ).json()["result"]
    return info["file_path"]


def download_telegram_file(file_id: str) -> str:
    file_path = get_file_path(file_id)
    url = f"{TELEGRAM_API}/{file_path}"
    content = requests.get(url, timeout=120).content

    suffix = "." + file_path.rsplit(".", 1)[-1] if "." in file_path else ".media"
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmpfile.write(content)
    tmpfile.close()
    return tmpfile.name


def handle_update(update: dict):
    global _last_update_id
    _last_update_id = update["update_id"]

    msg = update.get("message") or update.get("channel_post")
    if not msg:
        return

    chat_id = str(msg.get("chat", {}).get("id", ""))
    if not chat_id:
        return

    file_id = None
    file_kind = None
    if msg.get("audio"):
        file_id, file_kind = msg["audio"]["file_id"], "audio"
    elif msg.get("voice"):
        file_id, file_kind = msg["voice"]["file_id"], "voice"
    elif msg.get("video"):
        file_id, file_kind = msg["video"]["file_id"], "video"
    elif msg.get("video_note"):
        file_id, file_kind = msg["video_note"]["file_id"], "video note"

    text = msg.get("text") or msg.get("caption") or ""

    if file_id:
        print(f"Received {file_kind} file from {chat_id}, processing...")
        local_path = download_telegram_file(file_id)
        if is_media_file(local_path):
            _run(chat_id, local_path)
        else:
            print(f"Unsupported media type for file: {local_path}")
    elif text.strip().startswith(("http://", "https://")):
        print(f"Received URL from {chat_id}, processing...")
        _run(chat_id, text.strip())
    elif text.strip() == "/start":
        from notify import send_message

        send_message(
            chat_id,
            "Send me a YouTube/web link, a voice note, an audio file, or a video "
            "and I'll transcribe it, classify it, and save an action plan. "
            "Or just chat with me!",
        )
    elif text.strip():
        print(f"Received chat message from {chat_id}, replying...")
        _chat(chat_id, text.strip())


def _run(chat_id: str, source: str):
    try:
        result, saved_path = process(source, chat_id=chat_id)
        print(f"Done -> {result.get('branch')} | {saved_path}")
    except Exception as exc:
        print(f"Processing error: {exc}")
        from notify import send_message

        send_message(chat_id, f"❌ Error: {exc}")


def _chat(chat_id: str, message: str):
    try:
        from chat import chat_reply
        from notify import send_message

        reply = chat_reply(message)
        send_message(chat_id, reply)
    except Exception as exc:
        print(f"Chat error: {exc}")
        from notify import send_message

        send_message(chat_id, f"❌ Sorry, I couldn't respond: {exc}")


def listen():
    ensure_config()
    start_health_server()
    print(f"Bot listening... (API: {TELEGRAM_API.rsplit('/', 1)[0]}/)")
    while True:
        for update in get_updates():
            try:
                handle_update(update)
            except Exception as exc:
                print(f"handle_update error: {exc}")
        time.sleep(1)


if __name__ == "__main__":
    try:
        listen()
    except KeyboardInterrupt:
        print("\nBot stopped.")
        sys.exit(0)