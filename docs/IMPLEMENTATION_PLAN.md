# Implementation Plan

# Phase 0 — Repository Bootstrap

Create:

- pyproject.toml
- Python package
- tests structure
- Ruff configuration
- pytest configuration
- console script entry point

Verify:

python -m video_transcriber --help

or installed command:

video-transcriber --help

---

# Phase 1 — Domain Models

Implement typed models for:

- MediaInfo
- TranscriptionConfig
- ChunkInfo
- TranscriptWord
- TranscriptSegment
- ChunkResult
- JobManifest
- TranscriptionResult

Add unit tests.

---

# Phase 2 — Media Inspection

Implement:

- source validation
- ffmpeg availability check
- ffprobe availability check
- ffprobe metadata call
- duration extraction
- audio stream detection

Tests:

- nonexistent source
- invalid probe response
- missing audio stream
- valid metadata parsing

---

# Phase 3 — Hardware Detection

Implement:

- auto
- cpu
- cuda

Default compute type:

CUDA → float16
CPU → int8

Allow explicit override.

Tests must not require physical GPU.

---

# Phase 4 — Job Identity

Implement deterministic job ID.

Include:

- source absolute path
- size
- mtime
- model
- language
- chunk duration
- important inference settings

Test:

same configuration → same ID
changed source/configuration → different ID

---

# Phase 5 — Audio Chunking

Implement FFmpeg-based chunk extraction.

Default:

30 minutes

Preferred output:

mono
16 kHz
FLAC

Generate chunk manifest.

Test command construction separately.

Use a very small generated media file for integration test where practical.

---

# Phase 6 — Checkpoint System

Implement:

- manifest creation
- manifest loading
- manifest validation
- chunk result saving
- completed chunk detection
- atomic JSON writes

Test interruption/resume scenarios.

---

# Phase 7 — Whisper Integration

Implement faster-whisper model loading.

Implement:

- language
- VAD
- timestamps
- optional word timestamps

Avoid model loading during unit tests.

Provide injectable/mockable boundary.

---

# Phase 8 — Pipeline

Implement complete orchestrator:

validate
inspect
load/create job
chunk
detect completed work
load Whisper
transcribe pending chunks
persist result after every chunk
merge
export
cleanup

---

# Phase 9 — Export

Implement:

TXT
SRT
VTT
JSON

Unit test exact formatting.

Special care:

timestamps above one hour.

---

# Phase 10 — CLI

Implement:

video-transcriber transcribe SOURCE

Options:

--language
--model
--device
--compute-type
--chunk-minutes
--output-dir
--word-timestamps
--keep-cache
--force
--verbose

Use Rich for readable output.

---

# Phase 11 — Error UX

Provide explicit error messages for:

- FFmpeg missing
- source missing
- no audio
- model failure
- GPU failure
- transcription failure
- corrupted checkpoint

---

# Phase 12 — Integration Smoke Test

Create or generate a tiny audio sample.

Run pipeline without requiring a multi-GB test fixture.

Do not commit large binary fixtures.

---

# Phase 13 — Documentation

Update README with:

Installation
FFmpeg installation
Python setup
CPU usage
GPU usage
CLI examples
output format
resume explanation
troubleshooting

---

# Phase 14 — CI

Add GitHub Actions for:

ruff
pytest

Do not download Whisper models in normal CI.

---

# Final Verification

Run:

ruff check .
pytest
video-transcriber --help
video-transcriber transcribe --help

Perform small end-to-end transcription manually when environment supports it.

Only mark the MVP complete after all acceptance criteria pass.
