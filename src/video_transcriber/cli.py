import typer
from rich.console import Console

from .models import TranscriptionConfig
from .pipeline import run_pipeline

app = typer.Typer(help="Local Video Transcriber")
console = Console()

@app.callback()
def main():
    pass

@app.command()
def transcribe(
    source: str = typer.Argument(..., help="Path to the source media file."),
    language: str = typer.Option("auto", help="Language code (e.g., 'vi') or 'auto'."),
    model: str = typer.Option("large-v3", help="faster-whisper model name."),
    device: str = typer.Option("auto", help="'auto', 'cpu', or 'cuda'."),
    compute_type: str = typer.Option("auto", help="'auto', 'int8', 'float16'."),
    chunk_minutes: int = typer.Option(30, help="Duration of each audio chunk in minutes."),
    output_dir: str = typer.Option(None, help="Directory to save output files."),
    word_timestamps: bool = typer.Option(False, help="Include word-level timestamps."),
    keep_cache: bool = typer.Option(False, help="Keep intermediate chunk files."),
    force: bool = typer.Option(False, help="Force retranscription, ignoring checkpoints."),
    verbose: bool = typer.Option(False, help="Enable verbose logging."),
):
    """
    Transcribe a local video or audio file.
    """
    try:
        config = TranscriptionConfig(
            model=model,
            language=language,
            device=device,
            compute_type=compute_type,
            chunk_minutes=chunk_minutes,
            word_timestamps=word_timestamps,
            vad_enabled=True
        )
        
        run_pipeline(
            source_path=source,
            config=config,
            output_dir=output_dir,
            keep_cache=keep_cache,
            force=force,
            console=console
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            raise e
        raise typer.Exit(1)
