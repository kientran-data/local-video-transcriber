# Implementation Plan

## Overview & Status Summary

| Phase | Description | Status | Evidence / Notes |
|---|---|---|---|
| Phase 0 | Repository Bootstrap | **Completed** | `pyproject.toml`, console entry point, Ruff, Pytest |
| Phase 1 | Domain Models | **Completed** | `models.py` with Pydantic validation & resource fields |
| Phase 2 | Media Inspection | **Completed** | `media.py` ffprobe inspection, duration & stream detection |
| Phase 3 | Hardware Detection | **Completed** | `hardware.py` CUDA/cuBLAS detection & CPU fallback |
| Phase 4 | Job Identity | **Completed** | `checkpoint.py` deterministic SHA-256 hash |
| Phase 5 | Audio Chunking | **Completed** | `chunker.py` FFmpeg 16kHz mono FLAC streaming chunker |
| Phase 6 | Checkpoint System | **Completed** | `checkpoint.py` atomic JSON writes & resume detection |
| Phase 7 | Whisper Integration | **Completed** | `transcriber.py` faster-whisper wrapper with VAD & timestamps |
| Phase 8 | Pipeline Orchestration | **Completed** | `pipeline.py` end-to-end workflow execution |
| Phase 9 | Export Formats | **Completed** | `exporters/` for TXT, SRT, VTT, and JSON |
| Phase 10 | CLI Interface | **Completed** | `cli.py` with Typer & Rich console |
| Phase 11 | Error UX | **Completed** | Actionable error messages for missing tools/media |
| Phase 12 | Smoke Tests | **Completed** | Synthetic test in `tests/integration/test_pipeline.py` |
| Phase 13 | Documentation | **Completed** | README & docs synchronized with code |
| Phase 14 | Continuous Integration | **Completed** | `.github/workflows/ci.yml` running lint and tests |
| Phase 15 | Resource Management | **Completed** | `--low-resource`, CPU thread capping & GPU pacing |

---

# Phase 0 — Repository Bootstrap `[x]`

- [x] `pyproject.toml` created with dependencies (`faster-whisper`, `typer`, `rich`, `pydantic`).
- [x] Package structure configured under `src/video_transcriber`.
- [x] Entry point configured: `video-transcriber = "video_transcriber.cli:app"`.
- [x] Ruff and Pytest configured in `pyproject.toml`.
- [x] Verification: `python -m video_transcriber --help` and `video-transcriber --help` work.

---

# Phase 1 — Domain Models `[x]`

- [x] Implemented typed Pydantic models in `src/video_transcriber/models.py`:
  - `MediaInfo`: absolute path, size, mtime, duration, container, audio availability, sample rate, channels.
  - `TranscriptionConfig`: model, language, device, compute_type, chunk_minutes, vad_enabled, word_timestamps, cpu_threads, throttle_seconds, low_priority.
  - `ChunkInfo`: index, path, start_seconds, end_seconds, duration_seconds, status.
  - `TranscriptWord`: start, end, word, probability.
  - `TranscriptSegment`: start, end, text, words.
  - `ChunkResult`: chunk_index, segments.
  - `JobManifest`: job_id, source metadata, config, chunks list.
  - `TranscriptionResult`: job_id, source MediaInfo, config, segments list.
- [x] Validated via unit and integration tests.

---

# Phase 2 — Media Inspection `[x]`

- [x] Implemented in `src/video_transcriber/media.py`:
  - `check_ffmpeg_tools()` verifies `ffmpeg` and `ffprobe` availability on system PATH.
  - `inspect_media()` retrieves metadata using JSON probe output from `ffprobe`.
  - Validates that media exists, is readable, and contains at least one audio stream.
- [x] Fails early with actionable error message if no audio track exists.

---

# Phase 3 — Hardware Detection `[x]`

- [x] Implemented in `src/video_transcriber/hardware.py`:
  - Automatic detection policy:
    - CUDA available + cuBLAS DLL loaded: `device="cuda"`, `compute_type="float16"`.
    - Fallback: `device="cpu"`, `compute_type="int8"`.
  - Manual override supported via `--device` and `--compute-type`.
- [x] Handles Windows-specific cuBLAS 12 DLL availability check.

---

# Phase 4 — Job Identity `[x]`

- [x] Implemented in `src/video_transcriber/checkpoint.py`:
  - `generate_job_id()` computes a 16-character SHA-256 digest of:
    - Canonical source path, file size, modification timestamp.
    - Model name, language, chunk duration, VAD setting, word timestamp flag.
- [x] Ensures that identical runs reuse checkpoints, while configuration changes produce separate job workspaces.

---

# Phase 5 — Audio Chunking `[x]`

- [x] Implemented in `src/video_transcriber/chunker.py`:
  - Splits source media into chunks using FFmpeg stream seeking (`-ss` and `-t`).
  - Converts chunks directly into 16 kHz mono FLAC files without intermediate full-file WAV files.
  - Generates deterministic chunk files (`000000.flac`, `000001.flac`, etc.).
  - Default chunk duration is 30 minutes (configurable via `--chunk-minutes`).

---

# Phase 6 — Checkpoint System `[x]`

- [x] Implemented in `src/video_transcriber/checkpoint.py` with `CheckpointStore`:
  - Stores job state in `.transcriber-cache/<job-id>/`.
  - Saves `manifest.json` on initialization.
  - Persists each chunk result atomically as `results/<chunk_index:06d>.json` via temporary files and atomic rename.
  - Checks for completed chunk files on startup and skips re-transcription.
  - Cleaned up upon successful completion unless `--keep-cache` is specified.

---

# Phase 7 — Whisper Integration `[x]`

- [x] Implemented in `src/video_transcriber/transcriber.py`:
  - Wraps `faster_whisper.WhisperModel`.
  - Auto-detection or explicit language (`--language vi`, `en`, etc.).
  - Silero VAD enabled by default (`vad_filter=True`).
  - Supports segment timestamps and optional word-level timestamps.
  - Supports CPU thread limiting (`cpu_threads`).
  - Supports generator loop pacing (`throttle_seconds`).
  - PyAV >= 15 compatibility wrapper eliminates deprecated `metadata_errors` keyword crash.

---

# Phase 8 — Pipeline Orchestration `[x]`

- [x] Implemented in `src/video_transcriber/pipeline.py`:
  - Orchestrates: Inspect -> Hardware -> Job ID -> Chunk -> Transcribe -> Checkpoint -> Merge -> Export -> Cleanup.
  - Supports `--force` to discard prior cache and re-run.
  - Applies process priority class (`BelowNormal`) when low resource mode is requested.
  - Displays progress using Rich console.

---

# Phase 9 — Export `[x]`

- [x] Implemented in `src/video_transcriber/exporters/`:
  - `txt.py`: Plain text with `[HH:MM:SS]` timestamp prefixes.
  - `srt.py`: SubRip subtitle cues (`HH:MM:SS,mmm`).
  - `vtt.py`: WebVTT subtitle cues (`HH:MM:SS.mmm`).
  - `json_exporter.py`: Structured JSON containing metadata, config, and segments.
- [x] Formats timestamps above 1 hour correctly.
- [x] Strips leading/trailing whitespace and ignores empty cues.

---

# Phase 10 — CLI Interface `[x]`

- [x] Implemented in `src/video_transcriber/cli.py` using Typer and Rich:
  - `video-transcriber transcribe <SOURCE> [OPTIONS]`
  - Options:
    - `--language`: Language code or `auto` (default).
    - `--model`: Model size (default: `large-v3`).
    - `--device`: `auto`, `cpu`, or `cuda`.
    - `--compute-type`: `auto`, `int8`, `float16`.
    - `--chunk-minutes`: Default 30.
    - `--output-dir`: Custom output location.
    - `--word-timestamps`: Include word timings.
    - `--keep-cache`: Preserve audio chunk FLACs.
    - `--force`: Ignore cached results.
    - `--verbose`: Enable debug tracebacks.
    - `--low-resource`: Enable CPU and GPU throttling.
    - `--cpu-threads`: Limit CPU threads.
    - `--throttle-seconds`: Segment sleep pause.

---

# Phase 11 — Error UX `[x]`

- [x] Informative error messages for:
  - Missing FFmpeg or FFprobe on PATH with installation guidance.
  - Missing or unreadable source media files.
  - Media files without audio streams.
  - Invalid checkpoints or transcription exceptions.

---

# Phase 12 — Integration Smoke Test `[x]`

- [x] Implemented in `tests/integration/test_pipeline.py`:
  - Generates 1-second synthetic audio using FFmpeg (`aevalsrc`).
  - Mocks `WhisperTranscriber` to avoid model downloads during automated testing.
  - Validates that TXT, SRT, VTT, and JSON files are properly generated.
- [x] Real-world manual smoke tests completed for:
  - `FDownloader.vn_...mp4` (Vietnamese, ~5 min)
  - `YTSave_...mp3` (Vietnamese, ~19 min)
  - `the_coming_wave_2.mp3` (Vietnamese, ~55 min)
  - `the_coming_wave_3.mp3` (Vietnamese, ~53 min)
  - `the_comming_wave_4.mp3` (Vietnamese, ~16 min, low-resource)
  - `the_comming_wave_5.mp3` (Vietnamese, ~19 min, low-resource)
  - `tip_AI_1.mp3` (English, ~14 min, low-resource)

---

# Phase 13 — Documentation `[x]`

- [x] README updated with installation, FFmpeg setup, GPU/CPU guides, usage examples, and resource controls.
- [x] Architecture, Product Requirements, Implementation Plan, and Acceptance Criteria synchronized.

---

# Phase 14 — Continuous Integration `[x]`

- [x] Configured in `.github/workflows/ci.yml`:
  - Ubuntu latest runner with Python 3.11.
  - FFmpeg installation via `apt-get`.
  - Runs `ruff check .` and `pytest tests/`.
  - Does not download large model weights in CI.

---

# Phase 15 — Resource Management & Throttling `[x]`

- [x] Added `--low-resource` flag to prevent laptop thermal throttling and system freezing.
- [x] Sets process scheduling priority to `BelowNormal` so interactive apps stay responsive.
- [x] Restricts CPU threads to 2 by default in low-resource mode.
- [x] Paces segment yield in `transcriber.py` with configurable sleep intervals (default 0.25s).
- [x] Unit tested in `tests/unit/test_resource_limits.py`.

---

# Recommended Next Development Steps (Post-MVP)

1. **Batch Processing**:
   - Add `video-transcriber batch <DIRECTORY>` to transcribe all supported files in a folder sequentially.
2. **Speaker Diarization**:
   - Optional integration with `pyannote-audio` for speaker labels.
3. **Enhanced Markdown / Summary Output**:
   - Export structured Markdown with section headers or optional local LLM summarization.
