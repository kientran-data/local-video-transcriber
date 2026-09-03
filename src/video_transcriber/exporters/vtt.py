from pathlib import Path

from ..models import TranscriptionResult


def format_vtt_timestamp(seconds: float) -> str:
    """Format seconds to HH:MM:SS.mmm format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

def export_vtt(result: TranscriptionResult, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for seg in result.segments:
            start = format_vtt_timestamp(seg.start)
            end = format_vtt_timestamp(seg.end)
            text = seg.text.strip()
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
