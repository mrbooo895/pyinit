import os
import subprocess
import sys
import time
from rich.console import Console
from .utils import find_project_root, get_project_name
from .wrappers import error_handling

@error_handling
def install_project():
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print(f"[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)

    venv_dir = project_root / "venv"

    project_name = get_project_name(project_root)
    if not project_name:
        console.print(f"[dim yellow]\n[WARNING][/dim yellow] Could not determine project name from 'pyproject.toml'\n")

    if sys.platform == "win32":
        python_executable = venv_dir / "Scripts" / "python.exe"
        pip_executable = venv_dir / "Scripts" / "pip.exe"
    else:
        python_executable = venv_dir / "bin" / "python"
        pip_executable = venv_dir / "bin" / "pip"

    try:
        console.print(f"[bold green]    Fetching[/bold green] Required Build Modules")
        time.sleep(0.25)
        subprocess.run(
            [str(pip_executable), "install", "build", "wheel"],
            check=True, capture_output=True
        )

        console.print(f"[bold green]     Building[/bold green] package (application) '{project_name}'") 
        time.sleep(0.25)
        subprocess.run(
            [str(python_executable), "-m", "build"],
            cwd=project_root,
            check=True, capture_output=True
        )

        dist_dir = project_root / "dist"
        wheel_files = list(dist_dir.glob("*.whl"))
        if not wheel_files:
            console.print(f"[bold red][ERROR][/bold red] unable to find wheel modules")
            sys.exit(1)

        wheel_to_install = wheel_files[0]

        console.print(f"[bold green]      Installing[/bold green] project into system")
        time.sleep(0.25)
        subprocess.run(
            [str(pip_executable), "install", str(wheel_to_install), "--force-reinstall", "--break-system-packages"],
            check=True, capture_output=True
        )

        console.print(f"[bold green]\nSuccessfully[/bold green] installed package (application) '{project_name}'") 

    except subprocess.CalledProcessError as e:
        console.print(f"[bold red][ERROR][/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] {e}")
        sys.exit(1)
