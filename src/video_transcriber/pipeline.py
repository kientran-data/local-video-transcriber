import shutil
from pathlib import Path

from rich.console import Console

from .checkpoint import CheckpointStore, generate_job_id
from .chunker import chunk_media
from .exporters import export_all
from .hardware import determine_hardware
from .media import inspect_media
from .merger import merge_results
from .models import JobManifest, TranscriptionConfig
from .transcriber import WhisperTranscriber


class PipelineError(Exception):
    pass

def _apply_low_priority(console: Console) -> None:
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        console.print("[yellow]Applied low process priority (BelowNormal) to reduce CPU contention.[/yellow]")
    except Exception:
        try:
            import ctypes
            k32 = ctypes.windll.kernel32
            k32.GetCurrentProcess.restype = ctypes.c_void_p
            k32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
            k32.SetPriorityClass.restype = ctypes.c_bool
            k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)
            console.print("[yellow]Applied low process priority (BelowNormal).[/yellow]")
        except Exception:
            pass

def run_pipeline(
    source_path: str,
    config: TranscriptionConfig,
    output_dir: str,
    keep_cache: bool,
    force: bool,
    console: Console
) -> None:
    # 1. Inspect Media
    console.print(f"Inspecting media: [cyan]{source_path}[/cyan]")
    media = inspect_media(source_path)
    
    # 2. Hardware configuration
    device, compute_type = determine_hardware(config.device, config.compute_type)
    config.device = device
    config.compute_type = compute_type
    console.print(f"Media Duration: [green]{media.duration_seconds:.2f}s[/green]")
    console.print(f"Hardware: Device=[magenta]{device}[/magenta], Compute=[magenta]{compute_type}[/magenta]")
    
    if config.low_priority:
        _apply_low_priority(console)
    if config.throttle_seconds > 0 or config.cpu_threads > 0:
        console.print(
            f"Resource Limits: Throttle=[magenta]{config.throttle_seconds}s/segment[/magenta], "
            f"CPU Threads=[magenta]{config.cpu_threads or 'default'}[/magenta]"
        )

    # 3. Job Identity & Checkpointing
    job_id = generate_job_id(
        media.absolute_path,
        media.size_bytes,
        media.mtime,
        config
    )
    console.print(f"Job ID: [yellow]{job_id}[/yellow]")
    
    store = CheckpointStore()
    
    if force:
        console.print("[yellow]Force flag provided. Clearing previous job cache...[/yellow]")
        job_dir = store.get_job_dir(job_id)
        if job_dir.exists():
            shutil.rmtree(job_dir)
            
    manifest = store.load_manifest(job_id)
    
    if not manifest:
        console.print("Starting new job, chunking media...")
        store.get_job_dir(job_id).mkdir(parents=True, exist_ok=True)
        chunks_dir = store.get_chunks_dir(job_id)
        chunks_dir.mkdir(exist_ok=True)
        
        chunks = chunk_media(media, chunks_dir, config.chunk_minutes)
        
        manifest = JobManifest(
            job_id=job_id,
            source_path=media.absolute_path,
            source_size=media.size_bytes,
            source_mtime=media.mtime,
            config=config,
            chunks=chunks
        )
        store.init_job(manifest)
    else:
        console.print("[green]Resuming existing job from cache.[/green]")
        
    total_chunks = len(manifest.chunks)
    completed_indices = store.get_completed_chunk_indices(job_id)
    console.print(f"Total chunks: {total_chunks}. Completed: {len(completed_indices)}")
    
    # 4. Transcribe pending chunks
    pending_chunks = [c for c in manifest.chunks if c.index not in completed_indices]
    
    if pending_chunks:
        console.print("Loading Whisper model...")
        transcriber = WhisperTranscriber(config)
        
        for i, chunk in enumerate(pending_chunks, 1):
            console.print(f"Transcribing chunk {chunk.index + 1}/{total_chunks}...")
            
            try:
                result = transcriber.transcribe(chunk)
                store.save_chunk_result(job_id, result)
            except Exception as e:
                raise PipelineError(f"Transcription failed on chunk {chunk.index}: {e}")
                
    # 5. Merge Results
    console.print("Merging results...")
    all_results = []
    for chunk in manifest.chunks:
        res = store.load_chunk_result(job_id, chunk.index)
        if not res:
            raise PipelineError(f"Missing result for completed chunk {chunk.index}")
        all_results.append(res)
        
    final_result = merge_results(job_id, media, config, manifest.chunks, all_results)
    
    # 6. Export
    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = Path("output") / Path(source_path).stem
        
    out_path.mkdir(parents=True, exist_ok=True)
    console.print(f"Exporting to [cyan]{out_path}[/cyan]...")
    export_all(final_result, out_path)
    
    # 7. Cleanup
    if not keep_cache:
        console.print("Cleaning up generated media chunks...")
        chunks_dir = store.get_chunks_dir(job_id)
        if chunks_dir.exists():
            shutil.rmtree(chunks_dir)
            # Recreate empty chunks dir in case we need to resume? 
            # Actually, job is complete, we don't strictly need the flac files anymore.
            
    console.print("[bold green]Transcription complete![/bold green]")
