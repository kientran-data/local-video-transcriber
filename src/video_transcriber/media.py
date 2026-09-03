import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict

from .models import MediaInfo


class MediaError(Exception):
    pass

def check_dependencies() -> None:
    if not shutil.which("ffmpeg"):
        raise MediaError("FFmpeg was not found. Install it with: sudo apt install ffmpeg")
    if not shutil.which("ffprobe"):
        raise MediaError("ffprobe was not found. Install it with: sudo apt install ffmpeg")

def inspect_media(source_path: str) -> MediaInfo:
    check_dependencies()
    
    path = Path(source_path).resolve()
    if not path.exists():
        raise MediaError(f"Source file does not exist: {path}")
    if not path.is_file():
        raise MediaError(f"Source path is not a file: {path}")
        
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration,size,format_name:stream=codec_type,sample_rate,channels",
        "-print_format", "json",
        str(path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise MediaError(f"ffprobe failed to inspect media: {e.stderr}")
        
    try:
        data: Dict[str, Any] = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise MediaError("Failed to parse ffprobe output.")
        
    format_info = data.get("format", {})
    streams = data.get("streams", [])
    
    if not format_info:
        raise MediaError("No format information found in media.")
        
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    if not audio_streams:
        raise MediaError("No audio track found in media file.")
        
    first_audio = audio_streams[0]
    
    try:
        duration = float(format_info.get("duration", 0.0))
    except ValueError:
        raise MediaError("Invalid duration in media file.")
        
    size_bytes = int(format_info.get("size", path.stat().st_size))
    
    sample_rate = first_audio.get("sample_rate")
    if sample_rate:
        sample_rate = int(sample_rate)
        
    channels = first_audio.get("channels")
    if channels:
        channels = int(channels)
        
    return MediaInfo(
        absolute_path=str(path),
        size_bytes=size_bytes,
        mtime=path.stat().st_mtime,
        duration_seconds=duration,
        container_format=format_info.get("format_name", "unknown"),
        has_audio=True,
        sample_rate=sample_rate,
        channels=channels
    )
