import sys
import subprocess
import time
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

@error_handling
def show_dependency_graph():
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
    
    console.print("[bold green]    Checking[/bold green] for 'pipdeptree'")
    time.sleep(0.25)

    check_tool_cmd = [str(python_executable), "-c", "import pipdeptree"]
    tool_installed = subprocess.run(check_tool_cmd, capture_output=True).returncode == 0

    if not tool_installed:
        console.print(f"[bold green]     Installing[/bold green] Required Module 'pipdeptree'")
        install_cmd = [str(pip_executable), "install", "pipdeptree"]
        try:
            subprocess.run(install_cmd, check=True, capture_output=True)
            console.print("[bold green]      Successfully[/bold green] installed 'pipdeptree'")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red][ERROR][/bold red] Failed to install pipdeptree.")
            console.print(f"[red]{e.stderr.decode()}[/red]")
            sys.exit(1)
    else:
        console.print(f"[bold green]     Found[/bold green] Module 'pipdeptree'")
        time.sleep(0.5)
            
    console.print("[bold green]\nGenerating[/bold green] dependency graph...\n")
    time.sleep(1)

    graph_cmd = [str(python_executable), "-m", "pipdeptree"]
    
    subprocess.run(graph_cmd)
    
    console.print(f"\n[bold green]Graph[/bold green] generation completed.")