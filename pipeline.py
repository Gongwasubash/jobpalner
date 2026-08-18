import tempfile

from classify import classify_and_plan
from media import download_audio, is_media_file, is_url
from saver import save_plan
from transcribe import transcribe_audio


def process(source: str, chat_id: str = None) -> tuple:
    print(f"[1/4] Getting audio from: {source}")

    with tempfile.TemporaryDirectory() as tmpdir:
        if is_url(source):
            audio_path = download_audio(source, tmpdir)
        elif is_media_file(source):
            audio_path = source
        else:
            raise ValueError("Input must be a URL or a media file path")

        print("[2/4] Transcribing...")
        transcript = transcribe_audio(audio_path)
        print(f"Transcript ({len(transcript)} chars): {transcript[:200]}...")

        print("[3/4] Classifying and generating plan...")
        result = classify_and_plan(transcript)
        print(f"Branch: {result.get('branch')} | Title: {result.get('title')}")

        print("[4/4] Saving plan...")
        saved_path = save_plan(result, transcript)
        print(f"Saved to: {saved_path}")

        sheet_url = None
        try:
            from sheets import sync_if_enabled

            sheet_url = sync_if_enabled(result, transcript)
            if sheet_url:
                print(f"Synced to Google Sheets: {sheet_url}")
        except Exception as exc:
            print(f"Google Sheets sync failed (plan saved locally): {exc}")

        if chat_id:
            from notify import send_plan_notification

            send_plan_notification(chat_id, result, saved_path, sheet_url=sheet_url)

        return result, saved_path