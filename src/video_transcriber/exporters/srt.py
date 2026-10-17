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
        idx = 1
        for seg in result.segments:
            text = seg.text.strip()
            if not text:
                continue
            start = format_srt_timestamp(seg.start)
            end = format_srt_timestamp(seg.end)
            f.write(f"{idx}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
            idx += 1
