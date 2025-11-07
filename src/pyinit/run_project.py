import os
import sys
import subprocess
import time
from .utils import find_project_root
from .wrappers import error_handling
from rich.console import Console

console = Console()

@error_handling
def start_project(app_args: list = None):
    project_root = find_project_root()

    if not project_root:
        console.print(f"[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)
    
    project_name = project_root.name
    main_file = project_root / "src" / project_name / "main.py"
    venv_dir = project_root / "venv"

    if not main_file.exists():
        console.print(f"[bold red][ERROR][/bold red] main file '{main_file}' was not found.")
        sys.exit(1)

    if not venv_dir.exists():
        console.print(f"[bold red][ERROR][/bold red] Virtual Environment '{venv_dir.name}' not found\n-> Did You Create The Project Correctly?")
        sys.exit(1)

    if sys.platform == "win32":
        python_executable = venv_dir / "Scripts" / "python.exe"
    else:
        python_executable = venv_dir / "bin" / "python"

    console.print(f"[bold green]    Running[/bold green] package (application) '{project_name}'")
    time.sleep(0.25)

    try:
        run_cmd = [str(python_executable), str(main_file)] + app_args
        subprocess.run(run_cmd, check=True)
    except FileNotFoundError:
        console.print(f"\n[bold red][ERROR][/bold red] Python Executable '{python_executable}' Not Found\n-> The venv might be corrupted.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        console.print(f"\n[bold red][ERROR][/bold red] {e}")
