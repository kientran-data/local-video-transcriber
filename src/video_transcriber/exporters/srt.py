from pathlib import Path

from ..models import TranscriptionResult


def format_srt_timestamp(seconds: float) -> str:
    """Format seconds to HH:MM:SS,mmm format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def export_srt(result: TranscriptionResult, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result.segments, start=1):
            start = format_srt_timestamp(seg.start)
            end = format_srt_timestamp(seg.end)
            text = seg.text.strip()
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
