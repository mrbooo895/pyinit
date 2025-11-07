import os
import sys
import time
import subprocess
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

@error_handling
def install_module(module_to_install):
    console = Console()
    project_root = find_project_root()
    
    if not project_root:
        console.print(f"[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)
        
    module_name = module_to_install
    venv_dir = project_root / "venv"

    if not venv_dir.exists():
        console.print(f"[bold red][ERROR][/bold red] Virtual Environment '{venv_dir.name}' not found")
        sys.exit(1)
    
    if sys.platform == "win32":
        pip_executable = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_executable = venv_dir / "bin" / "pip"

    console.print(f"[bold green]    Installing[/bold green] module '{module_name}'")
    time.sleep(0.25)

    try: 
        subprocess.run([str(pip_executable), "install", module_name], check=True, capture_output=True)
        console.print(f"[bold green]Successfully[/bold green] Installed '{module_name}'")
    except Exception as e:
        console.print(f"\n[bold red][ERROR][/bold red] Failed To Install Module: {module_name}")