from typing import Protocol

from .models import (
    ChunkInfo,
    ChunkResult,
    TranscriptionConfig,
    TranscriptSegment,
    TranscriptWord,
)


class TranscriberProtocol(Protocol):
    def transcribe(self, chunk: ChunkInfo) -> ChunkResult:
        ...

class WhisperTranscriber:
    def __init__(self, config: TranscriptionConfig):
        self.config = config
        
        from faster_whisper import WhisperModel
        
        # For auto detection or specified
        self.language = None if config.language == "auto" else config.language
        
        # Initialize model
        self.model = WhisperModel(
            config.model,
            device=config.device,
            compute_type=config.compute_type
        )
        
    def transcribe(self, chunk: ChunkInfo) -> ChunkResult:
        segments_gen, info = self.model.transcribe(
            chunk.path,
            language=self.language,
            vad_filter=self.config.vad_enabled,
            word_timestamps=self.config.word_timestamps,
        )
        
        result_segments = []
        for s in segments_gen:
            words = None
            if self.config.word_timestamps and s.words:
                words = [
                    TranscriptWord(
                        start=w.start,
                        end=w.end,
                        word=w.word,
                        probability=w.probability
                    ) for w in s.words
                ]
                
            result_segments.append(
                TranscriptSegment(
                    start=s.start,
                    end=s.end,
                    text=s.text,
                    words=words
                )
            )
            
        return ChunkResult(
            chunk_index=chunk.index,
            segments=result_segments
        )
