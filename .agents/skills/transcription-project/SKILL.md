---
name: transcription-project
description: Implements, tests, debugs, or reviews the Local Video Transcriber Python project including faster-whisper, FFmpeg media processing, chunking, checkpoint/resume, subtitle export, and large-file transcription.
---

# Transcription Project Skill

Before implementing transcription-related work:

1. Read `/AGENTS.md`.
2. Read `/docs/PRODUCT_REQUIREMENTS.md`.
3. Read `/docs/ARCHITECTURE.md`.
4. Read `/docs/IMPLEMENTATION_PLAN.md`.
5. Read `/docs/ACCEPTANCE_CRITERIA.md`.

## Implementation Order

Work from infrastructure toward orchestration:

1. domain models
2. media inspection
3. hardware detection
4. job identity
5. chunking
6. checkpointing
7. Whisper boundary
8. segment merging
9. exporters
10. pipeline
11. CLI
12. tests
13. docs

## Large File Rules

Never:

- load full video into RAM
- create one giant temporary PCM WAV
- discard completed transcription work after a later failure

Prefer chunk-based processing.

## Resource Throttling Rules

When user requests low CPU/GPU usage or when working on shared/laptop systems:
- Pass `--low-resource` to CLI (or `--cpu-threads 2 --throttle-seconds 0.25`).
- Runs process at `BelowNormal` priority so interactive apps (IDEs, browsers) do not stutter.
- Paces segment iterations so GPU can drop to lower power states and stay cool.

## Testing Rule

Whisper model downloads must not occur in normal unit tests.

Design the inference boundary so it can be mocked:
- Integration tests patch `video_transcriber.pipeline.WhisperTranscriber`.
- Timestamp offset calculations and checkpoint recovery have dedicated unit tests.
- Resource throttling and configuration have dedicated unit tests.

## Completion Rule

After implementation:

- run Ruff: `ruff check .`
- run Pytest: `pytest`
- run CLI help: `python -m video_transcriber --help` and `python -m video_transcriber transcribe --help`
- inspect git diff: `git diff --stat`
- compare implementation against acceptance criteria

Do not report success until verification has been performed.
