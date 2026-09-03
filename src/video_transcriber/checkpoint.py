import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import List, Optional

from .models import ChunkResult, JobManifest, TranscriptionConfig


def generate_job_id(
    absolute_path: str,
    size_bytes: int,
    mtime: float,
    config: TranscriptionConfig
) -> str:
    """Generate a deterministic job ID based on input and configuration."""
    # Semantic elements that affect the result
    identity_data = {
        "path": absolute_path,
        "size": size_bytes,
        "mtime": mtime,
        "model": config.model,
        "language": config.language,
        "chunk_minutes": config.chunk_minutes,
        "vad_enabled": config.vad_enabled,
        "word_timestamps": config.word_timestamps
    }
    
    identity_str = json.dumps(identity_data, sort_keys=True)
    return hashlib.sha256(identity_str.encode("utf-8")).hexdigest()[:16]

class CheckpointStore:
    def __init__(self, cache_dir: str = ".transcriber-cache"):
        self.cache_dir = Path(cache_dir)
        
    def get_job_dir(self, job_id: str) -> Path:
        return self.cache_dir / job_id
        
    def get_manifest_path(self, job_id: str) -> Path:
        return self.get_job_dir(job_id) / "manifest.json"
        
    def get_chunks_dir(self, job_id: str) -> Path:
        return self.get_job_dir(job_id) / "chunks"
        
    def get_results_dir(self, job_id: str) -> Path:
        return self.get_job_dir(job_id) / "results"
        
    def init_job(self, manifest: JobManifest) -> None:
        job_dir = self.get_job_dir(manifest.job_id)
        job_dir.mkdir(parents=True, exist_ok=True)
        self.get_chunks_dir(manifest.job_id).mkdir(exist_ok=True)
        self.get_results_dir(manifest.job_id).mkdir(exist_ok=True)
        
        manifest_path = self.get_manifest_path(manifest.job_id)
        self._atomic_write(manifest_path, manifest.model_dump_json(indent=2))
        
    def load_manifest(self, job_id: str) -> Optional[JobManifest]:
        manifest_path = self.get_manifest_path(job_id)
        if not manifest_path.exists():
            return None
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return JobManifest(**data)
        except (json.JSONDecodeError, Exception):
            return None
            
    def save_chunk_result(self, job_id: str, result: ChunkResult) -> None:
        results_dir = self.get_results_dir(job_id)
        result_path = results_dir / f"{result.chunk_index:06d}.json"
        self._atomic_write(result_path, result.model_dump_json(indent=2))
        
    def load_chunk_result(self, job_id: str, chunk_index: int) -> Optional[ChunkResult]:
        result_path = self.get_results_dir(job_id) / f"{chunk_index:06d}.json"
        if not result_path.exists():
            return None
        try:
            with open(result_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ChunkResult(**data)
        except (json.JSONDecodeError, Exception):
            return None

    def get_completed_chunk_indices(self, job_id: str) -> List[int]:
        results_dir = self.get_results_dir(job_id)
        if not results_dir.exists():
            return []
            
        completed = []
        for path in results_dir.glob("*.json"):
            try:
                chunk_idx = int(path.stem)
                if self.load_chunk_result(job_id, chunk_idx) is not None:
                    completed.append(chunk_idx)
            except ValueError:
                pass
        return sorted(completed)
        
    def _atomic_write(self, path: Path, content: str) -> None:
        fd, temp_path = tempfile.mkstemp(dir=path.parent, prefix=".tmp", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, path)
        except Exception as e:
            os.remove(temp_path)
            raise e
