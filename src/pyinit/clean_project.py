import sys
import shutil
import time
from pathlib import Path
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

@error_handling
def clean_project():
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)

    patterns_to_remove = [
        "__pycache__",
        ".pytest_cache",
        "build",
        "dist",
        "*.egg-info",
        ".coverage",
    ]

    console.print("[bold green]    Searching[/bold green] for temporary and build-related files")
    time.sleep(0.25)
    
    paths_to_remove = []
    for pattern in patterns_to_remove:
        paths_to_remove.extend(project_root.rglob(pattern))

    if not paths_to_remove:
        console.print("[bold yellow][INFO][/bold yellow] Project is already clean. Nothing to remove.")
        sys.exit(0)

    console.print("[bold yellow][INFO][/bold yellow] The following files and directories will be permanently removed:")
    for path in paths_to_remove:
        relative_path = path.relative_to(project_root)
        console.print(f"  - {relative_path}")

    try:
        confirm = console.input(
            "\n - Are you sure you want to proceed? (y/N): "
        )
        if confirm.lower() != 'y':
            console.print("[bold yellow][INFO][/bold yellow] Operation cancelled by user.")
            sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        console.print("[bold yellow][WARNING][/bold yellow] Operation cancelled by user.")
        sys.exit(0)

    console.print(f"[bold green]\n     Cleaning[/bold green] project...")
    time.sleep(0.25)
    
    deleted_count = 0
    for path in paths_to_remove:
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            deleted_count += 1
        except OSError as e:
            console.print(f"[bold red][ERROR][/bold red] Could not remove {path}: {e}")

    console.print(f"\n[bold green]Successfully[/bold green] removed {deleted_count} items.")