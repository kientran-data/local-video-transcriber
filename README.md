# Local Video Transcriber

A local-first, memory-safe CLI application for transcribing long video and audio recordings using [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

Designed specifically for handling large files (hundreds of MBs to multi-gigabytes, multi-hour recordings) with deterministic checkpointing, resumable jobs, and support for Vietnamese and English speech.

---

## Key Features

- **Local-First & Private**: Transcribes locally on your machine. Your media and transcripts never leave your computer.
- **Large-File Safety**: Media is never loaded into RAM all at once, nor converted into one giant intermediate WAV file. Audio is streamed and chunked into memory-safe 16 kHz mono FLAC segments.
- **Resumable Checkpoints**: Each completed chunk is saved atomically to disk. If interrupted, the job picks up exactly where it left off without re-transcribing completed chunks.
- **Multi-Format Export**: Generates **TXT**, **SRT**, **VTT**, and **JSON** with accurate source-global timestamps.
- **Hardware Acceleration**: Automatic detection of NVIDIA CUDA (`float16`) with fallback to CPU (`int8`), configurable via CLI.
- **Resource Management & Laptop Mode**: `--low-resource` mode throttles CPU threads and paces GPU segment iterations to prevent laptop overheating, fan noise, and CPU contention.
- **Audio & Video Support**: Supports `MP4`, `MKV`, `MOV`, `WEBM`, `MP3`, `M4A`, `WAV`, `FLAC`.

---

## Architecture Pipeline

```text
Local Media (MP4 / MP3 / MKV / ...)
               │
               ▼
   1. Inspect Media (ffprobe)
               │
               ▼
   2. Hardware Detection (CUDA / CPU)
               │
               ▼
   3. Deterministic Job ID (SHA-256)
               │
               ▼
   4. Streamed Chunking (30m FLAC chunks)
               │
               ▼
   5. faster-whisper Inference (VAD + Timestamps)
               │
               ▼
   6. Atomic Per-Chunk Checkpoint (.transcriber-cache/)
               │
               ▼
   7. Global Timestamp Merge
               │
               ▼
   8. Exporters (TXT, SRT, VTT, JSON)
```

---

## Installation

### 1. Prerequisites

- **Python 3.11+**
- **FFmpeg & FFprobe** installed and accessible on your system `PATH`.

#### Installing FFmpeg

- **Ubuntu / Debian**:
  ```bash
  sudo apt update && sudo apt install -y ffmpeg
  ```
- **macOS (Homebrew)**:
  ```bash
  brew install ffmpeg
  ```
- **Windows (winget / scoop / manual)**:
  ```powershell
  winget install Gyan.FFmpeg
  ```
  *(Or download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/) and add its `bin/` directory to your system `PATH`.)*

### 2. Install the Package

Clone the repository and install in editable mode:

```bash
git clone https://github.com/kientran-data/local-video-transcriber.git
cd local-video-transcriber

# Create and activate virtual environment
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -e .

# Or with development dependencies (pytest, ruff):
pip install -e ".[dev]"
```

Verify installation:
```bash
video-transcriber --help
```

---

## Usage

### Basic Transcription

```bash
video-transcriber transcribe "meeting.mp4"
```

### Vietnamese Audio (e.g. Podcasts, Meetings)

```bash
video-transcriber transcribe "podcast_episode.mp3" --language vi --model large-v3
```

### English Audio

```bash
video-transcriber transcribe "lecture.mp4" --language en --model large-v3
```

### Resource Management / Laptop Low-Power Mode

When running transcription alongside other demanding tasks (e.g. IDEs, dev servers, browsers) or to keep your laptop cool and quiet:

```bash
video-transcriber transcribe "long_recording.mp3" --low-resource
```

What `--low-resource` does:
1. Lowers process priority to `BelowNormal` so Windows/Linux gives preference to interactive applications.
2. Limits CPU workers to 2 threads (`--cpu-threads 2`).
3. Inserts a 0.25s pause between decoded segments (`--throttle-seconds 0.25`), allowing GPU clock speeds to down-throttle and thermal levels to dissipate.

You can also customize these parameters explicitly:
```bash
video-transcriber transcribe "audio.mp3" --cpu-threads 2 --throttle-seconds 0.3
```

---

## CLI Reference

```text
Usage: video-transcriber transcribe [OPTIONS] SOURCE

Arguments:
  SOURCE                 Path to the source media file. [required]

Options:
  --language TEXT        Language code ('vi', 'en', etc.) or 'auto'. [default: auto]
  --model TEXT           faster-whisper model name. [default: large-v3]
  --device TEXT          'auto', 'cpu', or 'cuda'. [default: auto]
  --compute-type TEXT    'auto', 'int8', 'float16'. [default: auto]
  --chunk-minutes INT    Duration of each audio chunk in minutes. [default: 30]
  --output-dir TEXT      Directory to save output files.
  --word-timestamps      Include word-level timestamps in results.
  --keep-cache           Keep intermediate chunk audio files.
  --force                Force re-transcription, ignoring existing checkpoints.
  --verbose              Enable verbose error tracebacks.
  --low-resource         Limit CPU and GPU utilization (low priority, throttled).
  --cpu-threads INT      Limit CPU threads (0 = default/auto).
  --throttle-seconds     Pause in seconds between transcription segments.
  --help                 Show this message and exit.
```

---

## Output Layout

By default, transcripts are exported to `output/<source-name>/`:

```text
output/
└── my_podcast/
    ├── transcript.txt   # Clean plain text with [HH:MM:SS] markers
    ├── transcript.srt   # SubRip subtitle format
    ├── transcript.vtt   # WebVTT subtitle format
    └── transcript.json  # Full JSON schema with metadata and segment details
```

### Sample Output Formats

#### TXT
```text
[00:00:09] Chào mừng quý vị và các bạn đã đến với The Coming Wave Podcast.
[00:00:15] Hôm nay chúng ta sẽ thảo luận về sự phát triển của AI trong năm 2026.
```

#### SRT
```text
1
00:00:09,100 --> 00:00:14,800
Chào mừng quý vị và các bạn đã đến với The Coming Wave Podcast.

2
00:00:15,000 --> 00:00:20,500
Hôm nay chúng ta sẽ thảo luận về sự phát triển của AI trong năm 2026.
```

---

## Checkpointing & Resuming

Transcription jobs are assigned a deterministic SHA-256 Job ID based on the file's canonical path, size, modification timestamp, model, and language configuration.

Intermediary chunk results are atomically saved in:
```text
.transcriber-cache/<job-id>/
    ├── manifest.json
    ├── chunks/
    │   ├── 000000.flac
    │   └── 000001.flac
    └── results/
        ├── 000000.json
        └── 000001.json
```

If a transcription job is interrupted (Ctrl+C, crash, or shutdown):
- Re-running the same command detects the existing manifest and results.
- Completed chunks are skipped automatically.
- Once all chunks complete, results are merged and exported, and intermediate audio chunks are cleaned up.

---

## Development & Testing

### Running Tests
Unit and integration tests are isolated from model downloads:
```bash
pytest
```

### Code Formatting and Linting
```bash
ruff check .
```

### Continuous Integration
GitHub Actions workflow is configured in `.github/workflows/ci.yml` running lint and test suites on Ubuntu with FFmpeg.

---

## Troubleshooting

### 1. `FFmpeg was not found`
Ensure FFmpeg is installed and `ffmpeg -version` / `ffprobe -version` succeed in your terminal. Add the FFmpeg `bin/` directory to your system `PATH`.

### 2. Windows Console Unicode Characters
The application automatically reconfigures standard I/O streams to `utf-8`. If you are using Windows PowerShell or cmd, modern Windows Terminal is recommended for full UTF-8 emoji and font support.

### 3. CUDA / cuBLAS 12 on Windows
If CUDA is available on your machine but faster-whisper reports missing cuBLAS DLLs (`cublas64_12.dll`), ensure the NVIDIA CUDA runtime directory or standalone cuBLAS binaries are placed in your `PATH`. The application will safely fall back to CPU `int8` if CUDA DLLs are unresolvable.

### 4. PyAV Keyword Arguments
`src/video_transcriber/__init__.py` automatically patches PyAV to remove deprecated keyword arguments (`metadata_errors`), preventing crashes on PyAV >= 15.

---

## License

MIT License. See [LICENSE](LICENSE) for details.