import argparse
import sys

from config import ensure_config
from pipeline import process


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe a media URL/file, classify it, and save an action plan."
    )
    parser.add_argument("source", help="YouTube URL, any media URL, or local media file path")
    args = parser.parse_args()

    ensure_config()
    try:
        result, saved_path = process(args.source)
        print("\nDone.")
        print(f"Branch: {result.get('branch')}")
        print(f"Title: {result.get('title')}")
        print(f"File: {saved_path}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()