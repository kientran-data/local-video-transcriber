# Architecture

# 1. Architecture Style

Use a simple modular monolith.

This is a local CLI application.

Do not create services or distributed components.

---

# 2. Pipeline

Source media

    ↓

MediaInspector

    ↓

JobManager

    ↓

Chunker

    ↓

WhisperTranscriber

    ↓

CheckpointStore

    ↓

SegmentMerger

    ↓

Exporters

    ├── TXT
    ├── SRT
    ├── VTT
    └── JSON

---

# 3. Expected Source Layout

src/
└── video_transcriber/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── models.py
    ├── hardware.py
    ├── media.py
    ├── chunker.py
    ├── checkpoint.py
    ├── transcriber.py
    ├── merger.py
    ├── pipeline.py
    └── exporters/
        ├── __init__.py
        ├── txt.py
        ├── srt.py
        ├── vtt.py
        └── json_exporter.py

tests/
├── unit/
└── integration/

---

# 4. Pipeline Stages

## Stage A — Validate

Validate source.

Fail immediately if:

- file missing
- file unreadable
- unsupported media
- no audio track

---

## Stage B — Inspect

Use ffprobe to retrieve metadata.

Create MediaInfo.

---

## Stage C — Job Identification

Generate deterministic job ID.

Example concept:

SHA256(
    source absolute path
    source size
    source mtime
    model
    language
    chunk configuration
    transcription options
)

Do not depend on path alone.

---

## Stage D — Workspace

Create:

.transcriber-cache/<job-id>/

No temporary files should be placed next to source media.

---

# 5. Chunking Strategy

Do not first extract the entire movie into WAV.

Preferred:

source media
    ↓
FFmpeg
    ↓
30-minute audio chunks

For example:

chunks/
    000000.flac
    000001.flac
    000002.flac

The manifest defines authoritative timing.

Example conceptual manifest:

{
  "chunks": [
    {
      "index": 0,
      "path": ".../000000.flac",
      "start_seconds": 0,
      "end_seconds": 1800
    },
    {
      "index": 1,
      "path": ".../000001.flac",
      "start_seconds": 1800,
      "end_seconds": 3600
    }
  ]
}

FFmpeg command construction must be encapsulated and testable.

Never interpolate unsafe shell strings.

Prefer subprocess argument lists.

---

# 6. Whisper Layer

WhisperTranscriber receives:

- chunk path
- model configuration
- transcription configuration

Returns:

TranscriptionResult

WhisperTranscriber should not know about:

- checkpoints
- source video
- output filenames
- SRT
- VTT

---

# 7. Timestamp Merge

Whisper returns chunk-local time.

Example:

chunk start = 1800 sec

Whisper segment:

start = 12 sec
end = 18 sec

Final:

start = 1812 sec
end = 1818 sec

This logic must be independently unit tested.

---

# 8. Checkpoint Architecture

manifest.json records job metadata.

Each chunk result should be persisted independently:

results/
    000000.json
    000001.json
    000002.json

This is preferable to rewriting one massive JSON file after each chunk.

Final merge reads completed result files.

Use atomic write strategy:

write temporary file
→ fsync/close where reasonable
→ rename

This reduces corrupted checkpoints.

---

# 9. Resume Algorithm

On startup:

1. inspect source
2. calculate job ID
3. find matching manifest
4. validate manifest
5. inspect chunk result files
6. skip valid completed chunks
7. process remaining chunks
8. merge all results
9. export outputs

---

# 10. Hardware Detection

device=auto:

attempt CUDA availability detection.

If CUDA is usable:

device = cuda
compute_type = float16

otherwise:

device = cpu
compute_type = int8

Explicit user settings override automatic selection.

Do not claim GPU mode is active until model initialization succeeds.

---

# 11. Export Architecture

All exporters receive the same canonical merged transcription result.

Do not independently recalculate timestamps in every exporter.

Merger produces canonical global timestamps first.

Exporters only format data.

---

# 12. Dependency Direction

CLI
 ↓
Pipeline
 ↓
Domain/application modules

Exporters and infrastructure modules should not import CLI.

Avoid circular dependencies.

---

# 13. No Database

State is small and job-local.

JSON files are sufficient.

Do not introduce SQLite in MVP unless requirements change.

---

# 14. Disk Management

Chunk files can consume significant storage.

Provide cleanup behavior.

Default proposal:

- keep checkpoint/results
- remove generated media chunks after successful final export

Option:

--keep-cache

may preserve chunks.

Resume behavior must still be sensible if chunks were cleaned after a successful job.

---

# 15. Security

Never pass source filenames into:

shell=True

Use:

subprocess.run([...])

and argument arrays.

Never evaluate user-provided strings.

---

# 16. Performance

Optimize only where meaningful.

Priority:

1. correctness
2. resume reliability
3. transcription accuracy
4. memory safety
5. speed

Avoid premature concurrency.

MVP may transcribe chunks sequentially.

GPU inference is already computationally intensive.

Do not implement parallel chunk transcription until benchmarked.

---

# 17. Resource Management & Throttling

Running continuous large-model inference on laptops or shared development environments can cause excessive heat, loud cooling fans, and CPU starvation for other processes.

Architecture controls:
1. **Process Priority (`BelowNormal`)**: Uses `psutil` or Win32 `SetPriorityClass` to lower OS process scheduling priority, guaranteeing zero stutter for interactive processes (IDEs, browsers, node dev servers).
2. **CPU Thread Limiting (`cpu_threads`)**: Restricts faster-whisper/OpenMP CPU threads to a bounded pool (default 2 threads in low-resource mode) instead of claiming all logical cores.
3. **Segment Yield Pacing (`throttle_seconds`)**: Pauses between decoded segments in the generator loop (`time.sleep`). This introduces brief idle gaps between CUDA kernel launches, allowing the GPU to throttle down to lower P-states and drop thermal levels significantly (e.g. from 78°C to 67°C).

---

# 18. Platform Compatibility

1. **Windows Console Unicode**:
   Windows console streams (`stdout`/`stderr`) often default to legacy code pages (e.g. `cp1252`), causing `UnicodeEncodeError` when printing Vietnamese characters. `__init__.py` reconfigures streams to `utf-8`.
2. **PyAV >= 15 Keyword Compatibility**:
   Recent PyAV releases removed the `metadata_errors` keyword argument from `av.open`. A compatibility wrapper in `__init__.py` and `transcriber.py` ensures seamless audio decoding across library versions.
3. **cuBLAS 12 DLL Resolution**:
   On Windows, CUDA 12 requires `cublas64_12.dll` and `cublasLt64_12.dll`. `hardware.py` verifies both CUDA device accessibility and DLL loadability before routing to CUDA `float16`.
