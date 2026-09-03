from video_transcriber.merger import merge_results
from video_transcriber.models import (
    ChunkInfo,
    ChunkResult,
    MediaInfo,
    TranscriptionConfig,
    TranscriptSegment,
)


def test_merge_results():
    media = MediaInfo(
        absolute_path="/tmp/test.mp4",
        size_bytes=1000,
        mtime=123.45,
        duration_seconds=3600,
        container_format="mp4",
        has_audio=True
    )
    
    config = TranscriptionConfig(
        model="tiny", language="en", device="cpu", compute_type="int8", chunk_minutes=30
    )
    
    chunks = [
        ChunkInfo(index=0, path="/tmp/0.flac", start_seconds=0, end_seconds=1800, duration_seconds=1800),
        ChunkInfo(index=1, path="/tmp/1.flac", start_seconds=1800, end_seconds=3600, duration_seconds=1800)
    ]
    
    results = [
        ChunkResult(
            chunk_index=0,
            segments=[
                TranscriptSegment(start=10.0, end=15.0, text="First chunk segment.")
            ]
        ),
        ChunkResult(
            chunk_index=1,
            segments=[
                TranscriptSegment(start=5.0, end=10.0, text="Second chunk segment.")
            ]
        )
    ]
    
    final = merge_results("job1", media, config, chunks, results)
    
    assert final.job_id == "job1"
    assert len(final.segments) == 2
    
    # Check global timestamps
    assert final.segments[0].start == 10.0
    assert final.segments[0].end == 15.0
    
    assert final.segments[1].start == 1805.0
    assert final.segments[1].end == 1810.0
