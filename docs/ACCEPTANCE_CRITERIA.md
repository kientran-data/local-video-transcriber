# Acceptance Criteria

The MVP is complete only when every REQUIRED criterion below passes.

# CLI

- [x] `video-transcriber --help` works.
- [x] `video-transcriber transcribe --help` works.
- [x] A local source path can be supplied.
- [x] Paths containing spaces work.

# Media

- [x] Video files are accepted (MP4, MKV, MOV, WEBM).
- [x] Audio files are accepted (MP3, WAV, M4A, FLAC).
- [x] Missing files produce a clear error.
- [x] Media without audio produces a clear error.
- [x] Source files are never modified.

# Large File Safety

- [x] Entire media file is never loaded into RAM.
- [x] Entire source is not first converted into one giant WAV file.
- [x] Long media is processed using chunks.
- [x] Chunk duration is configurable via `--chunk-minutes`.

# Whisper

- [x] faster-whisper is used.
- [x] `large-v3` works when hardware supports it.
- [x] `--language vi` works.
- [x] automatic language detection works.
- [x] VAD is enabled by default.
- [x] CPU mode works (int8 default).
- [x] CUDA mode is supported (float16 default).

# Resource Control & Throttling

- [x] `--low-resource` mode throttles CPU and GPU to prevent overheating.
- [x] Process runs with `BelowNormal` priority to protect interactive applications.
- [x] CPU thread count is configurable via `--cpu-threads`.
- [x] Segment pause interval is configurable via `--throttle-seconds`.

# Resume

- [x] Job manifest is persisted.
- [x] Each completed chunk has persisted result.
- [x] Restart skips completed chunks.
- [x] Failed chunk remains incomplete.
- [x] Configuration changes cannot accidentally reuse incompatible results.
- [x] `--force` can intentionally reprocess.

# Timestamp

- [x] Chunk-local timestamps are converted to source-global timestamps.
- [x] Timestamp merge has unit tests (`tests/unit/test_merger.py`).
- [x] Media longer than one hour is formatted correctly.

# Output

- [x] TXT generated with readable timestamp markers.
- [x] SRT generated with valid SubRip cue timing.
- [x] VTT generated with WebVTT header and cue timings.
- [x] JSON generated with structured metadata and segment list.
- [x] Output location is printed to user.

# Reliability

- [x] A failure does not delete previously completed chunk results.
- [x] Checkpoint writes avoid partial JSON via atomic temporary file renaming.
- [x] Temporary files are isolated in `.transcriber-cache/<job-id>/`.

# Code Quality

- [x] Ruff passes (`ruff check .`).
- [x] pytest passes (`pytest`).
- [x] Unit and integration tests exist.
- [x] No large model files are committed.
- [x] No media chunks are committed.
- [x] No user transcripts are committed.

# Documentation

- [x] README contains install instructions.
- [x] README contains FFmpeg setup (Ubuntu and Windows).
- [x] README contains CPU example.
- [x] README contains NVIDIA GPU example.
- [x] README explains resume and checkpointing.
- [x] README explains output files and structure.
- [x] README explains resource management flags.

# Final Functional Test

Given local media files:

```bash
video-transcriber transcribe sample.mp4 --language vi
```

The application completes successfully and produces:

- `output/sample/transcript.txt`
- `output/sample/transcript.srt`
- `output/sample/transcript.vtt`
- `output/sample/transcript.json`

A second run with the same parameters recognizes existing completed work instead of needlessly retranscribing it.
