import subprocess
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from video_transcriber.models import ChunkResult, TranscriptionConfig, TranscriptSegment
from video_transcriber.pipeline import run_pipeline


def test_pipeline_integration(tmp_path: Path):
    # Create a tiny synthetic audio file using ffmpeg
    source_audio = tmp_path / "test_audio.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "aevalsrc=0:d=1",
        "-c:a", "pcm_s16le", "-ar", "16000", str(source_audio)
    ], check=True, capture_output=True)
    
    config = TranscriptionConfig(
        model="tiny", language="en", device="cpu", compute_type="int8", chunk_minutes=30
    )
    
    output_dir = tmp_path / "output"
    
    # Mock Whisper to avoid downloading models in CI
    with patch("video_transcriber.transcriber.WhisperTranscriber") as MockTranscriber:
        instance = MockTranscriber.return_value
        instance.transcribe.return_value = ChunkResult(
            chunk_index=0,
            segments=[TranscriptSegment(start=0.0, end=1.0, text="Mock transcribed text")]
        )
        
        run_pipeline(
            source_path=str(source_audio),
            config=config,
            output_dir=str(output_dir),
            keep_cache=False,
            force=False,
            console=Console(quiet=True)
        )
        
    assert (output_dir / "transcript.txt").exists()
    assert (output_dir / "transcript.srt").exists()
    assert (output_dir / "transcript.vtt").exists()
    assert (output_dir / "transcript.json").exists()
