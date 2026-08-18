import subprocess
from pathlib import Path

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".opus", ".flac", ".aac", ".webm", ".mp4", ".mkv", ".mov"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv"}


def is_url(source: str) -> bool:
    return source.startswith("http://") or source.startswith("https://")


def is_media_file(path: str) -> bool:
    return Path(path).suffix.lower() in AUDIO_EXTENSIONS


def download_audio(url: str, output_dir: str) -> str:
    out_template = str(Path(output_dir) / "audio.%(ext)s")
    subprocess.run(
        [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", out_template,
            "--no-playlist",
            url,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    out_dir = Path(output_dir)
    mp3s = sorted(out_dir.glob("audio.mp3"))
    if not mp3s:
        raise FileNotFoundError("yt-dlp did not produce an mp3 file")
    return str(mp3s[0])