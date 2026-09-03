from pathlib import Path

from .json_exporter import export_json
from .srt import export_srt
from .txt import export_txt
from .vtt import export_vtt


def export_all(result, output_dir: Path) -> None:
    export_txt(result, output_dir / "transcript.txt")
    export_srt(result, output_dir / "transcript.srt")
    export_vtt(result, output_dir / "transcript.vtt")
    export_json(result, output_dir / "transcript.json")
