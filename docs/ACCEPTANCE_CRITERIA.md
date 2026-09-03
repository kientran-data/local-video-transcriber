# Acceptance Criteria

The MVP is complete only when every REQUIRED criterion below passes.

# CLI

- [ ] `video-transcriber --help` works.
- [ ] `video-transcriber transcribe --help` works.
- [ ] A local source path can be supplied.
- [ ] Paths containing spaces work.

# Media

- [ ] Video files are accepted.
- [ ] Audio files are accepted.
- [ ] Missing files produce a clear error.
- [ ] Media without audio produces a clear error.
- [ ] Source files are never modified.

# Large File Safety

- [ ] Entire media file is never loaded into RAM.
- [ ] Entire source is not first converted into one giant WAV file.
- [ ] Long media is processed using chunks.
- [ ] Chunk duration is configurable.

# Whisper

- [ ] faster-whisper is used.
- [ ] `large-v3` works when hardware supports it.
- [ ] `--language vi` works.
- [ ] automatic language detection works.
- [ ] VAD is enabled by default.
- [ ] CPU mode works.
- [ ] CUDA mode is supported.

# Resume

- [ ] Job manifest is persisted.
- [ ] Each completed chunk has persisted result.
- [ ] Restart skips completed chunks.
- [ ] Failed chunk remains incomplete.
- [ ] Configuration changes cannot accidentally reuse incompatible results.
- [ ] `--force` can intentionally reprocess.

# Timestamp

- [ ] Chunk-local timestamps are converted to source-global timestamps.
- [ ] Timestamp merge has unit tests.
- [ ] Media longer than one hour is formatted correctly.

# Output

- [ ] TXT generated.
- [ ] SRT generated.
- [ ] VTT generated.
- [ ] JSON generated.
- [ ] Output location is printed to user.

# Reliability

- [ ] A failure does not delete previously completed chunk results.
- [ ] Checkpoint writes avoid partial JSON where practical.
- [ ] Temporary files are isolated from source media.

# Code Quality

- [ ] Ruff passes.
- [ ] pytest passes.
- [ ] Unit tests exist.
- [ ] No large model files are committed.
- [ ] No media chunks are committed.
- [ ] No user transcripts are committed.

# Documentation

- [ ] README contains install instructions.
- [ ] README contains Ubuntu FFmpeg setup.
- [ ] README contains CPU example.
- [ ] README contains NVIDIA GPU example.
- [ ] README explains resume.
- [ ] README explains output files.

# Final Functional Test

Given a local media file:

video-transcriber transcribe sample.mp4 --language vi

the application must complete successfully and produce:

output/sample/transcript.txt
output/sample/transcript.srt
output/sample/transcript.vtt
output/sample/transcript.json

A second run with the same parameters must recognize existing completed work instead of needlessly retranscribing it.
