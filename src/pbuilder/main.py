from pathlib import Path

from pbuilder.downloader import download_wheels
from pbuilder.log_manager import setup_logger
import typer

# Initialize the Typer app
# add_completion=True (default) enables the --install-completion flag
app = typer.Typer(
    name="pbuilder",
    help="Air-Gapped Python Environment Builder: Download and build wheels for offline use.",
    rich_markup_mode="rich"
)

@app.command()
def build(
    requirements: Path = typer.Option(
        ...,
        "--requirements", "-r",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the [bold green]requirements.txt[/bold green] file."
    ),
    output: Path = typer.Option(
        "./target",
        "--output", "-o",
        file_okay=False,
        dir_okay=True,
        writable=True,
        help="Directory to store downloaded wheels."
    ),
    logs: Path = typer.Option(
        "./logs",
        "--logs", "-l",
        help="Directory to store log files."
    )
):
    """
    Main command to download and cache python packages.
    """
    # 1. Path Normalization
    req_path = requirements.resolve()
    dest_path = output.resolve()
    log_path = logs.resolve()

    # 2. Ensure directories exist
    dest_path.mkdir(parents=True, exist_ok=True)
    log_path.mkdir(parents=True, exist_ok=True)

    # 3. Setup Logger
    setup_logger(log_dir=log_path)

    # 4. Run Logic
    try:
        typer.secho(f"🚀 Starting build process...", fg=typer.colors.CYAN, bold=True)
        download_wheels(str(req_path), str(dest_path))
        typer.secho(f"✨ Success! Wheels are in {dest_path}", fg=typer.colors.GREEN, bold=True)
    except Exception as e:
        typer.secho(f"💥 Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
