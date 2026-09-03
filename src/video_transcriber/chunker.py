import subprocess
from pathlib import Path
from typing import List

from .models import ChunkInfo, MediaInfo


class ChunkerError(Exception):
    pass

def chunk_media(
    media: MediaInfo,
    chunks_dir: Path,
    chunk_minutes: int
) -> List[ChunkInfo]:
    """
    Split media into audio chunks using FFmpeg's segment muxer.
    Outputs: mono, 16kHz, FLAC.
    Returns a list of ChunkInfo objects.
    """
    chunk_seconds = chunk_minutes * 60
    
    # We use segment muxer to split directly without a massive intermediate file.
    output_pattern = chunks_dir / "%06d.flac"
    
    cmd = [
        "ffmpeg",
        "-y",
        "-v", "error",
        "-i", media.absolute_path,
        "-vn",
        "-acodec", "flac",
        "-ac", "1",
        "-ar", "16000",
        "-f", "segment",
        "-segment_time", str(chunk_seconds),
        str(output_pattern)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise ChunkerError(f"FFmpeg chunking failed: {e.stderr}")
        
    # FFmpeg will produce 000000.flac, 000001.flac, etc.
    chunks = []
    chunk_files = sorted(list(chunks_dir.glob("*.flac")))
    
    if not chunk_files:
        raise ChunkerError("FFmpeg produced no chunks.")
        
    for i, chunk_path in enumerate(chunk_files):
        # We can probe for exact duration, but for most speech cases 
        # using index * chunk_seconds is sufficient for the global offset.
        # The true length is needed to know if it's the last shorter chunk.
        
        # Simple duration estimation (last chunk will just be whatever remains)
        start_seconds = i * chunk_seconds
        remaining = media.duration_seconds - start_seconds
        duration_seconds = min(float(chunk_seconds), remaining)
        
        # In reality, if we need precise duration of the flac, we could ffprobe it.
        # For this MVP, assuming exact boundaries is usually fine for segmenting.
        chunks.append(
            ChunkInfo(
                index=i,
                path=str(chunk_path),
                start_seconds=start_seconds,
                end_seconds=start_seconds + duration_seconds,
                duration_seconds=duration_seconds,
                status="pending"
            )
        )
        
    return chunks
