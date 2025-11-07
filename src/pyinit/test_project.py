import sys
import subprocess
import time
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

@error_handling
def run_tests(pytest_args: list):
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)

    venv_dir = project_root / "venv"
    if not venv_dir.exists():
        console.print("[bold red][ERROR][/bold red] Virtual environment 'venv' not found.")
        sys.exit(1)
        
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        console.print("[bold yellow][INFO][/bold yellow] No 'tests' directory found. Nothing to test.")
        sys.exit(0)

    if sys.platform == "win32":
        python_executable = venv_dir / "Scripts" / "python.exe"
        pip_executable = venv_dir / "Scripts" / "pip.exe"
    else:
        python_executable = venv_dir / "bin" / "python"
        pip_executable = venv_dir / "bin" / "pip"

    console.print(f"[bold green]    Starting[/bold green] to test project")
    time.sleep(0.5)

    check_pytest_cmd = [str(python_executable), "-c", "import pytest"]
    pytest_installed = subprocess.run(check_pytest_cmd, capture_output=True).returncode == 0

    if not pytest_installed:
        console.print(f"[bold green]     Installing[/bold green] 'pytest' into current venv")
        time.sleep(0.5)
        install_pytest_cmd = [str(pip_executable), "install", "pytest"]
        try:
            subprocess.run(install_pytest_cmd, check=True, capture_output=True)
            console.print("[bold green]    Successfully[/bold green] installed 'pytest'.")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red][ERROR][/bold red] Failed to install pytest.")
            console.print(f"[red]{e.stderr.decode()}[/red]")
            sys.exit(1)

    console.print(f"[bold green]Running[/bold green] tests\n")
    time.sleep(0.5)
    
    run_tests_cmd = [str(python_executable), "-m", "pytest"] + pytest_args
    
    try:
        subprocess.run(run_tests_cmd, cwd=project_root)
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] An unexpected error occurred while running tests: {e}")
        sys.exit(1)