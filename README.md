# Local Video Transcriber

A local-first CLI application for transcribing large video and audio files using faster-whisper.

The project is designed primarily for long-form Vietnamese speech and large local media files such as 800 MB, 2 GB, or multi-hour recordings.

## Core Goal

Given a local media file:

```text
video/audio
    ↓
inspect media
    ↓
prepare audio chunks
    ↓
transcribe chunks
    ↓
checkpoint progress
    ↓
merge transcript
    ↓
export
```

The application must produce:

* TXT
* SRT
* VTT
* JSON

without uploading the user's source media to an external transcription service.

## Primary Use Case

```bash
video-transcriber transcribe "/path/to/video.mp4"
```

Example:

```bash
video-transcriber transcribe \
  "/home/user/Videos/meeting.mp4" \
  --language vi \
  --model large-v3
```

## Product Principles

1. Local-first.
2. Large-file friendly.
3. Resumable.
4. Deterministic output structure.
5. Clear progress reporting.
6. CPU and NVIDIA GPU support.
7. Simple CLI UX.
8. No unnecessary services or databases.
9. No web backend in MVP.
10. Reliability is more important than cleverness.

## MVP Features

* Local video/audio input
* MP4, MKV, MOV, WEBM, MP3, M4A, WAV support
* Media validation
* Media metadata inspection
* Long-file chunking
* faster-whisper transcription
* Vietnamese language option
* automatic language detection
* VAD
* CPU support
* NVIDIA CUDA support
* automatic hardware selection
* checkpoint after each completed chunk
* resume interrupted jobs
* progress display
* TXT export
* SRT export
* VTT export
* JSON export
* configurable output directory
* configurable Whisper model

## Explicitly Out of Scope for MVP

Do NOT implement:

* user authentication
* cloud storage
* cloud deployment
* SaaS architecture
* REST API
* database
* Docker orchestration
* Kubernetes
* speaker diarization
* translation
* web frontend
* distributed processing
* queues such as Celery/Kafka
* microservices

These may be considered after the CLI MVP is stable.

## Documentation

Before modifying implementation, read:

1. `AGENTS.md`
2. `docs/PRODUCT_REQUIREMENTS.md`
3. `docs/ARCHITECTURE.md`
4. `docs/IMPLEMENTATION_PLAN.md`
5. `docs/ACCEPTANCE_CRITERIA.md`

The documentation above is the source of truth for the MVP.