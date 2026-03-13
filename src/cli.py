# WARNING: template code, may need edits

"""Command-line interface for AIS Data Cleaner."""

from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.cleaner import AISCleaner
from src.config import load_config

app = typer.Typer(
    name="ais-cleaner",
    help="AIS Data Cleaner - Clean and denoise AIS data from Parquet files",
    add_completion=False,
)
console = Console()


@app.command()
def clean(
    input_path: Path = typer.Argument(..., help="Input Parquet file or directory"),
    output_path: Optional[Path] = typer.Option(None, "--output", "-o", help="Output path"),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
    report: bool = typer.Option(True, "--report/--no-report", help="Generate cleaning report"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
):
    """Clean AIS data from Parquet file(s)."""
    # Configure logging
    if verbose:
        logger.remove()
        logger.add(lambda msg: console.print(msg, end=""), level="DEBUG")
    
    # Load configuration
    config = load_config(config_path) if config_path else load_config()
    
    # Initialize cleaner
    cleaner = AISCleaner(config)
    
    # Process file or directory
    if input_path.is_file():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Cleaning data...", total=None)
            
            try:
                cleaner.clean_file(input_path, output_path, generate_report=report)
                console.print("[green]✓[/green] Cleaning complete!")
            except Exception as e:
                console.print(f"[red]✗[/red] Error: {e}")
                raise typer.Exit(code=1)
    
    elif input_path.is_dir():
        try:
            cleaner.clean_directory(input_path, output_path)
            console.print("[green]✓[/green] Batch cleaning complete!")
        except Exception as e:
            console.print(f"[red]✗[/red] Error: {e}")
            raise typer.Exit(code=1)
    
    else:
        console.print(f"[red]✗[/red] Invalid input path: {input_path}")
        raise typer.Exit(code=1)


@app.command()
def validate(
    input_path: Path = typer.Argument(..., help="Input Parquet file"),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
):
    """Validate AIS data without cleaning."""
    config = load_config(config_path) if config_path else load_config()
    cleaner = AISCleaner(config)
    
    console.print(f"Validating: {input_path}")
    
    try:
        df = cleaner.read_parquet(input_path)
        valid_mask = cleaner.validator.validate_all(df)
        
        valid_count = valid_mask.sum()
        invalid_count = (~valid_mask).sum()
        
        console.print(f"\n[green]Valid records:[/green] {valid_count:,}")
        console.print(f"[red]Invalid records:[/red] {invalid_count:,}")
        console.print(f"[yellow]Validity:[/yellow] {valid_count/len(df)*100:.2f}%")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def info(
    input_path: Path = typer.Argument(..., help="Input Parquet file"),
):
    """Display information about AIS Parquet file."""
    try:
        import pyarrow.parquet as pq
        
        parquet_file = pq.ParquetFile(input_path)
        
        console.print(f"\n[bold]File:[/bold] {input_path}")
        console.print(f"[bold]Rows:[/bold] {parquet_file.metadata.num_rows:,}")
        console.print(f"[bold]Columns:[/bold] {parquet_file.metadata.num_columns}")
        console.print(f"[bold]Size:[/bold] {input_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        console.print("\n[bold]Schema:[/bold]")
        for field in parquet_file.schema:
            console.print(f"  {field.name}: {field.type}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
