import sys
import subprocess
import time
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

@error_handling
def lock_dependencies():
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)

    venv_dir = project_root / "venv"
    if not venv_dir.exists():
        console.print("[bold red][ERROR][/bold red] Virtual environment 'venv' not found.")
        sys.exit(1)
        
    requirements_file = project_root / "requirements.txt"

    if sys.platform == "win32":
        pip_executable = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_executable = venv_dir / "bin" / "pip"

    console.print(f"[bold green]    Locking[/bold green] dependencies to '{requirements_file.name}'")
    time.sleep(0.5)

    freeze_cmd = [str(pip_executable), "freeze"]
    
    try:
        result = subprocess.run(freeze_cmd, check=True, capture_output=True, text=True)
        
        with open(requirements_file, "w") as f:
            f.write(result.stdout)
            
        console.print(f"[bold green]Successfully[/bold green] created '{requirements_file.name}'.")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red][ERROR][/bold red] Failed to run 'pip freeze'.")
        console.print(f"[red]{e.stderr}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] An unexpected error occurred: {e}")
        sys.exit(1)