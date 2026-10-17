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
        
        try:
            import av
            _orig_av_open = av.open

            def _safe_av_open(*args, **kwargs):
                kwargs.pop("metadata_errors", None)
                return _orig_av_open(*args, **kwargs)

            av.open = _safe_av_open
        except (ImportError, AttributeError):
            pass

        from faster_whisper import WhisperModel
        
        # For auto detection or specified
        self.language = None if config.language == "auto" else config.language
        
        # Initialize model
        self.model = WhisperModel(
            config.model,
            device=config.device,
            compute_type=config.compute_type,
            cpu_threads=config.cpu_threads if config.cpu_threads > 0 else 0
        )
        
    def transcribe(self, chunk: ChunkInfo) -> ChunkResult:
        import time

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

            if self.config.throttle_seconds > 0:
                time.sleep(self.config.throttle_seconds)
            
        return ChunkResult(
            chunk_index=chunk.index,
            segments=result_segments
        )
