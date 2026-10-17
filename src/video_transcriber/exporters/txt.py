from pathlib import Path

from ..models import TranscriptionResult


def format_timestamp(seconds: float) -> str:
    """Format seconds to [HH:MM:SS] format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"[{h:02d}:{m:02d}:{s:02d}]"

def export_txt(result: TranscriptionResult, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for seg in result.segments:
            text = seg.text.strip()
            if not text:
                continue
            ts = format_timestamp(seg.start)
            f.write(f"{ts} {text}\n")
