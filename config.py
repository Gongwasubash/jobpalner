import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
PLANS_BASE_FOLDER = Path(os.getenv("PLANS_BASE_FOLDER", "./plans"))

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "").strip()
GOOGLE_CREDENTIALS_FILE = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", str(BASE_DIR / "credentials.json")))
GOOGLE_TOKEN_FILE = Path(os.getenv("GOOGLE_TOKEN_FILE", str(BASE_DIR / "token.json")))
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "").strip()
GOOGLE_TOKEN_JSON = os.getenv("GOOGLE_TOKEN_JSON", "").strip()
GOOGLE_DRIVE_SYNC = os.getenv("GOOGLE_DRIVE_SYNC", "true").strip().lower() in ("1", "true", "yes")

WHISPER_MODEL = "whisper-large-v3"
CLASSIFIER_MODEL = "openai/gpt-oss-120b"


def ensure_config():
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if missing:
        raise SystemExit(
            "Missing environment variable(s): "
            + ", ".join(missing)
            + "\nCopy .env.example to .env and fill in your keys."
        )