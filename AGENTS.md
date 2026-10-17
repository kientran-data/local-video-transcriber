# AGENTS.md

## Role

You are the primary software engineer responsible for implementing and maintaining this repository.

This repository contains a local-first large-media transcription application.

Before writing code, read:

- README.md
- docs/PRODUCT_REQUIREMENTS.md
- docs/ARCHITECTURE.md
- docs/IMPLEMENTATION_PLAN.md
- docs/ACCEPTANCE_CRITERIA.md

Treat those documents as the product specification.

---

# Core Engineering Rules

## 1. Do Not Overengineer

The MVP is a local Python CLI application.

Do not introduce:

- databases
- Redis
- Celery
- Kafka
- REST APIs
- web servers
- frontend frameworks
- cloud services
- microservices
- Docker Compose

unless explicitly requested later.

Prefer the smallest architecture that satisfies the requirements.

---

## 2. Large Files Must Be First-Class

The application is specifically intended to handle:

- hundreds-of-megabytes video files
- multi-gigabyte media files
- recordings lasting multiple hours

Never design an implementation that loads the entire media file into memory.

Operate on file paths and streams.

Temporary processing must occur chunk by chunk.

---

## 3. Jobs Must Be Resumable

Long transcription jobs may run for hours.

A crash or interruption must not require retranscribing completed chunks.

Each completed chunk must have a persisted checkpoint.

On restart, completed chunks must be detected and skipped.

Checkpoint writes must be atomic whenever practical.

---

## 4. Source Media Must Never Be Modified

Never overwrite, rename, move, truncate, or modify the source media file.

All temporary and generated files must be stored separately.

---

## 5. Local-First Privacy

MVP transcription happens locally.

Do not upload user media or transcript content to external APIs.

Downloading a public model on first use is acceptable.

---

# Technology

Use:

- Python 3.11+
- faster-whisper
- FFmpeg / ffprobe
- Typer
- Rich
- pytest
- Ruff

Avoid adding dependencies unless they provide meaningful value.

---

# Architecture

Implementation should approximately follow:

src/video_transcriber/
    __init__.py
    cli.py
    models.py
    hardware.py
    media.py
    chunker.py
    transcriber.py
    checkpoint.py
    merger.py
    pipeline.py
    exporters/
        __init__.py
        txt.py
        srt.py
        vtt.py
        json_exporter.py

Tests should approximately mirror implementation:

tests/
    unit/
    integration/

Do not create unnecessary abstraction layers.

---

# Module Responsibilities

## cli.py

Only responsible for:

- parsing CLI arguments
- displaying user-facing messages
- invoking application pipeline

Business logic must not live in CLI handlers.

## config.py

Responsible for configuration and defaults.

## hardware.py

Responsible for:

- detecting CUDA availability
- choosing CPU/GPU
- determining compute type

Default policy:

CUDA available:
    device=cuda
    compute_type=float16

Otherwise:
    device=cpu
    compute_type=int8

Manual CLI options must be able to override automatic selection.

## media.py

Responsible for:

- validating source path
- inspecting media
- obtaining duration
- obtaining streams and metadata
- checking FFmpeg/ffprobe availability

## chunker.py

Responsible for:

- splitting long media/audio into processable chunks
- preserving exact chunk start offsets
- producing a manifest

Chunks must have deterministic names.

Example:

000000.flac
000001.flac
000002.flac

Do not create one giant intermediate WAV file.

## transcriber.py

Responsible only for Whisper inference.

It must not contain export logic.

It must expose structured transcription segments.

## checkpoint.py

Responsible for:

- job state
- completed chunk tracking
- persisted partial results
- safe resume

## pipeline.py

Application orchestration.

Responsible for:

inspect
→ create/load job
→ chunk
→ transcribe unfinished chunks
→ checkpoint
→ merge
→ export

## exporters/

Output formatting only.

---

# Data Model

Use typed Python data structures.

Prefer dataclasses or Pydantic models where validation materially helps.

Core structures should include concepts similar to:

MediaInfo
ChunkInfo
TranscriptSegment
WordTimestamp
JobManifest
TranscriptionResult

Do not pass arbitrary unstructured dictionaries across the entire codebase.

---

# Chunking

Default chunk duration:

30 minutes

Make chunk duration configurable.

Chunk manifests must contain:

- chunk index
- source path
- chunk file path
- start_seconds
- end_seconds
- duration_seconds
- status

Global timestamps must be calculated from:

global_timestamp =
chunk_start_seconds + local_segment_timestamp

Do not reset timestamps when merging chunks.

---

# Checkpointing

A transcription job must have a stable job identifier.

Job identity must consider at least:

- resolved source path
- file size
- source modification time
- model
- language
- relevant transcription configuration

Changing transcription settings should not incorrectly reuse incompatible previous results.

Suggested cache layout:

.transcriber-cache/
    <job-id>/
        manifest.json
        chunks/
        results/

Example:

.transcriber-cache/
    abc123/
        manifest.json
        chunks/
            000000.flac
            000001.flac
        results/
            000000.json
            000001.json

If `000000.json` is valid and marked complete, that chunk should not be retranscribed.

---

# Output Layout

Default output:

output/
    <source-name>/
        transcript.txt
        transcript.srt
        transcript.vtt
        transcript.json

The application must not silently overwrite unrelated output.

---

# Transcription Defaults

Default model:

large-v3

Default language:

auto detection

User can specify:

--language vi

Enable VAD by default.

Word timestamps should be supported.

Do not invent transcript text when Whisper returns no speech.

---

# CLI UX

Target interface:

video-transcriber transcribe SOURCE

Useful options include:

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
--low-resource
--cpu-threads
--throttle-seconds

---

# Resource Management & Throttling

To prevent laptop overheating and CPU/GPU contention during long jobs:

- `--low-resource`: Automatically enables `BelowNormal` process priority class, limits CPU threads to 2, and sleeps 0.25s between segment iterations.
- `--cpu-threads`: Explicitly limits CPU worker threads (prevents 100% utilization across all CPU cores).
- `--throttle-seconds`: Paces segment generator iterations (`time.sleep`) allowing GPU to lower clock speeds and dissipate thermal build-up.

---

# Platform & Compatibility

- **Windows Console UTF-8**: `src/video_transcriber/__init__.py` reconfigures `sys.stdout` and `sys.stderr` to UTF-8 to prevent `UnicodeEncodeError` when printing Vietnamese text or filenames.
- **cuBLAS 12 on Windows**: `hardware.py` verifies CUDA and cuBLAS DLL availability (`cublas64_12.dll`) before selecting CUDA.
- **PyAV >= 15**: Compatibility patch removes `metadata_errors` argument from `av.open` calls.

Provide:

video-transcriber --help

and:

video-transcriber transcribe --help

Errors must be actionable.

Bad:

Error occurred.

Good:

FFmpeg was not found. Install it with:
sudo apt install ffmpeg

---

# Error Handling

Handle at minimum:

- source file does not exist
- unsupported media
- unreadable media
- FFmpeg unavailable
- ffprobe failure
- model loading failure
- CUDA unavailable
- CUDA out-of-memory
- transcription failure
- corrupted checkpoint
- insufficient disk space where detectable
- output write failure

Never silently ignore failed chunks.

---

# Logging

Normal user output should be clean.

Support verbose/debug logging.

Do not flood normal output with library internals.

---

# Testing

No feature is complete until tests pass.

Tests must not download large Whisper models.

Mock or isolate inference for ordinary unit tests.

Unit tests should cover:

- timestamp formatting
- chunk offset merging
- deterministic job IDs
- checkpoint loading/saving
- resume behavior
- config validation
- output generation

Integration tests should cover a small synthetic media sample when practical.

---

# Quality Gates

Before declaring implementation complete:

1. Run Ruff.
2. Run pytest.
3. Run CLI help.
4. Run a small end-to-end smoke test.
5. Verify output files exist.
6. Verify resumed jobs skip completed chunks.
7. Update README when commands change.

---

# Git Rules

Keep commits logically scoped.

Never commit:

- model weights
- video files
- audio chunks
- cache files
- generated transcripts
- virtual environments
- secrets

---

# Definition of Done

A task is not complete merely because code was written.

It is complete only when:

- implementation exists
- tests exist
- tests pass
- lint passes
- CLI is executable
- documentation reflects reality
- acceptance criteria are satisfied

When encountering ambiguity, prefer the simplest solution consistent with the specification instead of inventing additional product scope.
