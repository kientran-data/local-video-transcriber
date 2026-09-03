from typing import List, Optional

from pydantic import BaseModel


class MediaInfo(BaseModel):
    absolute_path: str
    size_bytes: int
    mtime: float
    duration_seconds: float
    container_format: str
    has_audio: bool
    sample_rate: Optional[int] = None
    channels: Optional[int] = None

class TranscriptionConfig(BaseModel):
    model: str
    language: str
    device: str
    compute_type: str
    chunk_minutes: int
    vad_enabled: bool = True
    word_timestamps: bool = False

class ChunkInfo(BaseModel):
    index: int
    path: str
    start_seconds: float
    end_seconds: float
    duration_seconds: float
    status: str = "pending"  # "pending", "completed", "failed"

class TranscriptWord(BaseModel):
    start: float
    end: float
    word: str
    probability: float

class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str
    words: Optional[List[TranscriptWord]] = None

class ChunkResult(BaseModel):
    chunk_index: int
    segments: List[TranscriptSegment]

class JobManifest(BaseModel):
    job_id: str
    source_path: str
    source_size: int
    source_mtime: float
    config: TranscriptionConfig
    chunks: List[ChunkInfo]

class TranscriptionResult(BaseModel):
    job_id: str
    source: MediaInfo
    config: TranscriptionConfig
    segments: List[TranscriptSegment]
