from typing import List

from .models import (
    ChunkInfo,
    ChunkResult,
    MediaInfo,
    TranscriptionConfig,
    TranscriptionResult,
    TranscriptSegment,
    TranscriptWord,
)


def merge_results(
    job_id: str,
    media: MediaInfo,
    config: TranscriptionConfig,
    manifest_chunks: List[ChunkInfo],
    chunk_results: List[ChunkResult]
) -> TranscriptionResult:
    """
    Merge chunk-local transcription results into a single result with global timestamps.
    """
    # Create a mapping of chunk index to its global start time
    start_times = {chunk.index: chunk.start_seconds for chunk in manifest_chunks}
    
    global_segments = []
    
    for result in sorted(chunk_results, key=lambda x: x.chunk_index):
        global_offset = start_times.get(result.chunk_index, 0.0)
        
        for segment in result.segments:
            global_words = None
            if segment.words:
                global_words = [
                    TranscriptWord(
                        start=w.start + global_offset,
                        end=w.end + global_offset,
                        word=w.word,
                        probability=w.probability
                    ) for w in segment.words
                ]
                
            global_segments.append(
                TranscriptSegment(
                    start=segment.start + global_offset,
                    end=segment.end + global_offset,
                    text=segment.text,
                    words=global_words
                )
            )
            
    return TranscriptionResult(
        job_id=job_id,
        source=media,
        config=config,
        segments=global_segments
    )
