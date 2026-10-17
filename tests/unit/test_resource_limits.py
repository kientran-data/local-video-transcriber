import time
from unittest.mock import MagicMock, patch

from video_transcriber.models import ChunkInfo, TranscriptionConfig
from video_transcriber.transcriber import WhisperTranscriber


def test_resource_limits_config():
    config = TranscriptionConfig(
        model="tiny",
        language="vi",
        device="cpu",
        compute_type="int8",
        chunk_minutes=30,
        cpu_threads=2,
        throttle_seconds=0.1,
        low_priority=True
    )
    assert config.cpu_threads == 2
    assert config.throttle_seconds == 0.1
    assert config.low_priority is True


def test_transcriber_throttle(tmp_path):
    config = TranscriptionConfig(
        model="tiny",
        language="vi",
        device="cpu",
        compute_type="int8",
        chunk_minutes=30,
        throttle_seconds=0.05
    )

    chunk = ChunkInfo(
        index=0,
        path=str(tmp_path / "dummy.flac"),
        start_seconds=0.0,
        end_seconds=10.0,
        duration_seconds=10.0
    )

    with patch("faster_whisper.WhisperModel") as MockModel:
        mock_instance = MockModel.return_value
        seg1 = MagicMock(start=0.0, end=2.0, text="Hello", words=None)
        seg2 = MagicMock(start=2.0, end=4.0, text="World", words=None)
        mock_instance.transcribe.return_value = ([seg1, seg2], MagicMock())

        transcriber = WhisperTranscriber(config)
        start_t = time.perf_counter()
        result = transcriber.transcribe(chunk)
        elapsed = time.perf_counter() - start_t

        assert len(result.segments) == 2
        # Should have slept at least 2 * 0.05 = 0.1s
        assert elapsed >= 0.09
