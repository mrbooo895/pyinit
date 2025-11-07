import sys
import time
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

def update_gitignore(project_root, console):
    gitignore_path = project_root / ".gitignore"
    env_entry = "\n# Environment variables\n.env\n"
    
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write(env_entry)
        return

    with open(gitignore_path, "r") as f:
        content = f.read()
    
    if ".env" not in content:
        with open(gitignore_path, "a") as f:
            f.write(env_entry)
        console.print("[dim yellow]       - Added[/dim yellow] '.env' to .gitignore")

@error_handling
def manage_env(vars_to_set: list):
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)
        
    env_file_path = project_root / ".env"
    env_vars = {}

    if env_file_path.exists():
        with open(env_file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

    console.print(f"[bold green]    Updating[/bold green] '.env' file")
    time.sleep(0.25)
    
    for var in vars_to_set:
        if '=' not in var:
            console.print(f"[bold red][ERROR][/bold red] Invalid format: '{var}'. Expected KEY=VALUE.")
            continue
        key, value = var.split('=', 1)
        env_vars[key] = value
        console.print(f"[bold green]     Setting[/bold green] [yellow]{key}[/yellow] to [cyan]'{value}'[/cyan]")

    with open(env_file_path, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    update_gitignore(project_root, console)
    
    console.print("\n[bold green]Successfully[/bold green] updated '.env' file.")