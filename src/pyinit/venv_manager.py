import sys
import venv
import shutil
import time
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

@error_handling
def manage_venv(action: str):
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)
        
    venv_dir = project_root / "venv"

    if action == "create":
        create_virtual_env(console, venv_dir)
    elif action == "remove":
        remove_virtual_env(console, venv_dir)

def create_virtual_env(console: Console, venv_dir):
    console.print(f"[bold green]     Creating[/bold green] virtual environment")
    time.sleep(0.25)
    
    if venv_dir.exists():
        console.print("[bold red][ERROR][/bold red] A 'venv' directory already exists.")
        console.print("       - If you want to recreate it, run 'pyinit venv remove' first.")
        sys.exit(1)
    
    try:
        venv.create(venv_dir, with_pip=True)
        console.print("[bold green]Successfully[/bold green] created virtual environment.")
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] Failed to create virtual environment: {e}")
        sys.exit(1)

def remove_virtual_env(console: Console, venv_dir):
    console.print(f"[bold yellow]     Removing[/bold yellow] virtual environment")
    time.sleep(0.25)

    if not venv_dir.exists() or not venv_dir.is_dir():
        console.print("[bold yellow][INFO][/bold yellow] No 'venv' directory found to remove.")
        sys.exit(1)
    
    try:
        confirm = console.input(
            "[bold red][CRITICAL][/bold red] This is a destructive action. Are you sure you want to remove the entire 'venv' directory? (y/N): "
        )
        if confirm.lower() == 'y':
            console.print(f"[bold green]      Deleting[/bold green] directory '{venv_dir.name}'")
            time.sleep(0.25)
            shutil.rmtree(venv_dir)
            console.print("[bold green]Successfully[/bold green] removed virtual environment.")
        else:
            console.print("[bold yellow][INFO][/bold yellow] Operation cancelled by user.")
            sys.exit(0)
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] Failed to remove virtual environment: {e}")
        sys.exit(1)