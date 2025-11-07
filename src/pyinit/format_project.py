import sys
import subprocess
import time
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

@error_handling
def format_project():
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
    
    check_formatters_cmd = [str(python_executable), "-c", "import black, isort"]
    formatters_installed = subprocess.run(check_formatters_cmd, capture_output=True).returncode == 0

    console.print(f"[bold green]    Starting[/bold green] to format project's structure")
    time.sleep(0.5)

    if not formatters_installed:
        console.print(f"[bold green]     Installing[/bold green] Required formatting modules 'black' and 'isort'")
        time.sleep(0.5)
        install_cmd = [str(pip_executable), "install", "black", "isort"]
        try:
            subprocess.run(install_cmd, check=True, capture_output=True)
            console.print("[bold green]    Successfully[/bold green] installed formatting tools.")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red][ERROR][/bold red] Failed to install formatting tools.")
            console.print(f"[red]{e.stderr.decode()}[/red]")
            sys.exit(1)
            
    targets_to_format = [project_root / "src", project_root / "tests"]
    formatted_something = False

    for target_dir in targets_to_format:
        if target_dir.exists() and target_dir.is_dir():
            console.print(f"[bold green]     Formatting[/bold green] '{target_dir.relative_to(project_root)}/'")
            time.sleep(0.5)
            
            isort_cmd = [str(python_executable), "-m", "isort", str(target_dir)]
            black_cmd = [str(python_executable), "-m", "black", str(target_dir)]
            
            subprocess.run(isort_cmd, capture_output=True)
            subprocess.run(black_cmd, capture_output=True)
            formatted_something = True

    if formatted_something:
        console.print("\n[bold green]Successfully[/bold green] Formatted Codebase")
    else:
        console.print("[bold yellow][INFO][/bold yellow] No source 'src' or test 'tests' directories found to format.")