import sys
import subprocess
import time
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

@error_handling
def lint_project():
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)

    venv_dir = project_root / "venv"
    if not venv_dir.exists():
        console.print("[bold red][ERROR][/bold red] Virtual environment 'venv' not found.")
        sys.exit(1)

    if sys.platform == "win32":
        python_executable = venv_dir / "Scripts" / "python.exe"
        pip_executable = venv_dir / "Scripts" / "pip.exe"
    else:
        python_executable = venv_dir / "bin" / "python"
        pip_executable = venv_dir / "bin" / "pip"
    
    console.print("[bold green]    Checking[/bold green] for linter 'ruff'")
    time.sleep(0.25)
    
    check_linter_cmd = [str(python_executable), "-c", "import ruff"]
    linter_installed = subprocess.run(check_linter_cmd, capture_output=True).returncode == 0

    if not linter_installed:
        console.print(f"[bold green]     Installing[/bold green] Required Linting Module 'ruff'")
        install_cmd = [str(pip_executable), "install", "ruff"]
        try:
            subprocess.run(install_cmd, check=True, capture_output=True)
            console.print("[bold green]Successfully[/bold green] installed 'ruff'")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red][ERROR][/bold red] Failed to install ruff.")
            console.print(f"[red]{e.stderr.decode()}[/red]")
            sys.exit(1)
    else:
        console.print(f"[bold green]     Found[/bold green] Linting Module 'ruff'")
            
    targets_to_lint = []
    src_dir = project_root / "src"
    tests_dir = project_root / "tests"
    
    if src_dir.exists():
        targets_to_lint.append(src_dir)
    if tests_dir.exists():
        targets_to_lint.append(tests_dir)

    if not targets_to_lint:
        console.print("[bold yellow][INFO][/bold yellow] No source 'src' or test 'tests' directories found to lint.")
        sys.exit(0)

    console.print("[bold green]Running[/bold green] linter on codebase\n")
    time.sleep(0.5)

    lint_cmd = [str(python_executable), "-m", "ruff", "check"] + [str(p) for p in targets_to_lint]
    
    subprocess.run(lint_cmd)
    
    console.print(f"\n[bold green]Linting[/bold green] process completed.")