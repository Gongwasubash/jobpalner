import requests

from config import TELEGRAM_BOT_TOKEN


def send_message(chat_id: str, text: str):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=30,
    ).raise_for_status()


def send_plan_notification(chat_id: str, result: dict, saved_path: str, sheet_url: str = None, drive_link: str = None):
    msg = (
        "✅ *Plan saved!*\n\n"
        f"📁 Branch: `{result.get('branch')}`\n"
        f"📝 Title: {result.get('title')}\n"
        f"🎯 Confidence: {int(float(result.get('confidence', 0)) * 100)}%\n"
        f"🏷 Tags: {', '.join(result.get('tags', []))}\n\n"
        f"📄 File: `{saved_path}`"
    )
    if sheet_url:
        msg += f"\n📊 [View in Google Sheets]({sheet_url})"
    if drive_link:
        msg += f"\n💾 [View .md in Google Drive]({drive_link})"
    send_message(chat_id, msg)