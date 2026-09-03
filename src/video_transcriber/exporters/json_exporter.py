from pathlib import Path

from ..models import TranscriptionResult


def export_json(result: TranscriptionResult, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(indent=2))
