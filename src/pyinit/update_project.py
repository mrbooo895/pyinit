import sys
import subprocess
import time
from rich.console import Console
from .utils import find_project_root, get_project_dependencies
from .wrappers import error_handling

@error_handling
def update_dependencies(upgrade: bool = False):
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
        pip_executable = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_executable = venv_dir / "bin" / "pip"

    if upgrade:
        console.print("[bold green]    Upgrading[/bold green] project dependencies...")
        time.sleep(0.25)
        
        project_deps = get_project_dependencies(project_root)
        
        if not project_deps:
            console.print("[bold yellow][INFO][/bold yellow] No project dependencies found in 'pyproject.toml' to upgrade.")
            sys.exit(0)

        console.print(f"[bold green]     Found[/bold green] {len(project_deps)} direct dependencies to check.")
        
        try:
            upgrade_cmd = [str(pip_executable), "install", "--upgrade"] + project_deps
            subprocess.run(upgrade_cmd, check=True)
            console.print(f"\n[bold green]Successfully[/bold green] updated project dependencies.")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red][ERROR][/bold red] Failed to upgrade packages.")
            console.print(f"[red]{e.stderr.decode()}[/red]")
            sys.exit(1)
            
    else:
        console.print("[bold green]    Checking[/bold green] for outdated packages...")
        time.sleep(0.25)
        
        check_cmd = [str(pip_executable), "list", "--outdated"]
        
        try:
            subprocess.run(check_cmd)
            console.print("\n[bold green]Run:[/bold green]\n     'pyinit update --upgrade' to upgrade project dependencies.")
        except Exception as e:
            console.print(f"[bold red][ERROR][/bold red] Failed to check for updates: {e}")
            sys.exit(1)