import os
import subprocess
from pathlib import Path

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".opus", ".flac", ".aac", ".webm", ".mp4", ".mkv", ".mov"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv"}

# Auto-detect deno for YouTube JS runtime (fixes most 403s)
_DENO_PATH = None
for p in [
    r"C:\Users\acer\AppData\Local\Microsoft\WinGet\Packages\DenoLand.Deno_Microsoft.Winget.Source_8wekyb3d8bbwe\deno.exe",
    "/usr/bin/deno",
    "/usr/local/bin/deno",
    "/opt/deno/bin/deno",
]:
    if os.path.exists(p):
        _DENO_PATH = p
        break


def is_url(source: str) -> bool:
    return source.startswith("http://") or source.startswith("https://")


def is_media_file(path: str) -> bool:
    return Path(path).suffix.lower() in AUDIO_EXTENSIONS


def download_audio(url: str, output_dir: str) -> str:
    out_template = str(Path(output_dir) / "audio.%(ext)s")
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", out_template,
        "--no-playlist",
        url,
    ]
    if _DENO_PATH:
        cmd.insert(1, f"deno:{_DENO_PATH}")
        cmd.insert(1, "--js-runtimes")
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        if "HTTP Error 403" in stderr or "Forbidden" in stderr:
            raise RuntimeError(
                "YouTube download failed (403 Forbidden). This video may be region-blocked, "
                "copyright-restricted, or temporarily unavailable from this server. "
                "Try a different link, or send the audio file directly."
            )
        raise RuntimeError(f"yt-dlp failed: {stderr[-500:]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("YouTube download timed out (5 min). Try a shorter video.")

    out_dir = Path(output_dir)
    mp3s = sorted(out_dir.glob("audio.mp3"))
    if not mp3s:
        raise FileNotFoundError("yt-dlp did not produce an mp3 file")
    return str(mp3s[0])