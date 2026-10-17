# Product Requirements

## 1. Product

Local Video Transcriber is a command-line application that converts speech contained in local video or audio files into structured text and subtitle files.

---

# 2. Primary User Story

As a user,

I want to provide the path of a large video,

so that the application transcribes its spoken content locally,

without requiring me to upload the original video to an external service.

Example source:

800 MB MP4
2-hour meeting
Vietnamese speech

Expected result:

TXT
SRT
VTT
JSON

---

# 3. Core Command

The canonical command should be:

video-transcriber transcribe <SOURCE>

Example:

video-transcriber transcribe "/data/video.mp4"

Vietnamese:

video-transcriber transcribe "/data/video.mp4" --language vi

---

# 4. Input Requirements

Supported MVP formats:

Video:
- mp4
- mkv
- mov
- webm

Audio:
- mp3
- m4a
- wav
- flac

The implementation should rely on actual media probing rather than extension checks alone where practical.

There is no artificial application-level 800 MB file limit.

The pipeline must not read the entire source media into RAM.

---

# 5. Media Inspection

Before transcription, retrieve:

- absolute source path
- source file size
- duration
- container format
- audio stream availability
- sample rate when available
- channel information when available

If no audio stream exists, stop with a clear error.

---

# 6. Processing

Long media should be processed in chunks.

Default:

30-minute chunks

Chunk duration must be configurable.

The application should create normalized audio chunks appropriate for speech transcription.

Preferred normalized characteristics:

- mono
- 16 kHz
- FLAC or another appropriate speech-friendly format

Do not create a complete uncompressed WAV copy of a multi-hour source before chunking.

---

# 7. Transcription

Use faster-whisper.

Required:

- large-v3 support
- language auto detection
- explicit Vietnamese language
- VAD
- timestamps
- optional word timestamps

Device options:

auto
cpu
cuda

Compute type options should remain compatible with faster-whisper/CTranslate2.

Auto defaults:

CUDA:
float16

CPU:
int8

---

# 7.1 Resource Control & Throttling

To prevent laptop overheating and CPU/GPU contention during long jobs:

- `--low-resource`: Sets process priority to BelowNormal, limits CPU threads to 2, and sleeps 0.25s between segment iterations.
- `--cpu-threads <N>`: Restricts number of CPU threads used by faster-whisper.
- `--throttle-seconds <float>`: Inserts a pause between segment decoding to allow GPU thermal dissipation.

---

# 8. Progress

User should be able to see:

- media duration
- selected model
- selected device
- number of chunks
- current chunk
- completed chunks
- current progress
- output location

Example:

Source: meeting.mp4
Duration: 02:41:13
Model: large-v3
Device: CUDA
Chunks: 6

Transcribing chunk 3/6...

---

# 9. Resume

After each chunk:

- save structured result
- mark chunk complete
- persist state

If application stops after chunk 4/6:

next run should start at chunk 5/6.

It must not retranscribe chunks 1-4 unless:

- --force is used
- source changed
- incompatible transcription configuration changed
- checkpoint is invalid

---

# 10. Transcript Representation

Internal transcript segment should include:

- start
- end
- text

Optional:

- words
- word start
- word end
- probability/confidence metadata when available

All final timestamps must use global source-media time.

---

# 11. TXT Output

Readable plain transcript.

Example:

[00:00:03] Xin chào mọi người.
[00:00:07] Hôm nay chúng ta sẽ bắt đầu cuộc họp.

---

# 12. SRT Output

Must generate valid standard SRT:

1
00:00:03,000 --> 00:00:06,500
Xin chào mọi người.

2
00:00:07,000 --> 00:00:11,500
Hôm nay chúng ta sẽ bắt đầu cuộc họp.

---

# 13. VTT Output

Must generate valid WebVTT.

---

# 14. JSON Output

JSON is the canonical machine-readable output.

Suggested shape:

{
  "source": {},
  "transcription": {},
  "segments": []
}

Source metadata should be included.

---

# 15. Failure Recovery

If one chunk fails:

- do not mark it completed
- preserve previous completed chunks
- show actionable error
- allow rerunning job

---

# 16. Privacy

The application processes source media locally.

No external transcription API is part of MVP.

---

# 17. Non-Goals

MVP does not include:

- speaker diarization
- speaker identification
- cloud transcription
- collaboration
- web frontend
- cloud storage
- REST API
- authentication
- billing
- translation

---

# 18. Future Features

Potential later phases:

- speaker diarization
- desktop UI
- drag and drop
- batch folder transcription
- transcript search
- summary generation
- chapter detection
- automatic meeting notes
