import sys
import time
import subprocess
import datetime
from pathlib import Path
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

def run_command(command, cwd):
    try:
        result = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, check=True, encoding='utf-8'
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_venv_info(project_root):
    venv_dir = project_root / "venv"
    if not venv_dir.exists():
        return "[dim]N/A[/dim]", "0"
        
    if sys.platform == "win32":
        python_executable = venv_dir / "Scripts" / "python.exe"
        pip_executable = venv_dir / "Scripts" / "pip.exe"
    else:
        python_executable = venv_dir / "bin" / "python"
        pip_executable = venv_dir / "bin" / "pip"
        
    if not python_executable.exists():
        return "[dim]N/A[/dim]", "0"

    version = run_command([str(python_executable), "--version"], project_root)
    packages_output = run_command([str(pip_executable), "list"], project_root)
    packages_count = len(packages_output.splitlines()) - 2 if packages_output and len(packages_output.splitlines()) > 2 else 0
    
    return version or "[dim]N/A[/dim]", str(packages_count)

def get_project_stats(project_root):
    total_files = 0
    total_lines = 0
    latest_mod_time = 0.0
    src_dir = project_root / "src"
    
    if src_dir.is_dir():
        py_files = list(src_dir.rglob("*.py"))
        total_files = len(py_files)
        for path in py_files:
            try:
                mod_time = path.stat().st_mtime
                if mod_time > latest_mod_time:
                    latest_mod_time = mod_time
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    total_lines += len(f.readlines())
            except Exception:
                continue
    
    last_modified = datetime.datetime.fromtimestamp(latest_mod_time).strftime('%Y-%m-%d %H:%M:%S') if latest_mod_time > 0 else "[dim]N/A[/dim]"
    return total_files, total_lines, last_modified

@error_handling
def project_info():
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)

    pyproject_path = project_root / "pyproject.toml"
    
    console.print(f"[bold green]    Generating[/bold green] Information Table")
    time.sleep(0.25)
    
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        project_data = data.get("project", {})
    except (tomllib.TOMLDecodeError, FileNotFoundError):
        console.print(f"[bold red][ERROR][/bold red] Could not read or parse '{pyproject_path.name}'.")
        sys.exit(1)

    console.print(f"  Name           : {project_data.get('name', '[dim]N/A[/dim]')}")
    console.print(f"  Version        : {project_data.get('version', '[dim]N/A[/dim]')}")
    console.print(f"  Description    : {project_data.get('description', '[dim]N/A[/dim]')}")
    authors = ", ".join([a.get("name", "") for a in project_data.get("authors", [])])
    console.print(f"  Authors        : {authors or '[dim]N/A[/dim]'}")
    license_info = project_data.get("license", {})
    license_text = license_info.get("text") if isinstance(license_info, dict) else str(license_info)
    console.print(f"  License        : {license_text or '[dim]N/A[/dim]'}")

    venv_python, venv_packages = get_venv_info(project_root)
    files, lines, last_mod = get_project_stats(project_root)
    creation_time = datetime.datetime.fromtimestamp(project_root.stat().st_ctime).strftime('%Y-%m-%d %H:%M:%S')

    console.print(f"  Project Path   : {project_root}")
    console.print(f"  Created On     : {creation_time}")
    console.print(f"  Last Modified  : {last_mod} (in src)")
    console.print(f"  Python Req.    : {project_data.get('requires-python', '[dim]N/A[/dim]')}")
    console.print(f"  Venv Python    : {venv_python}")
    console.print(f"  Venv Packages  : {venv_packages} installed")
    console.print(f"  Files (in src) : {files}")
    console.print(f"  Lines (in src) : {lines:,}")
    
    branch = run_command(["git", "branch", "--show-current"], project_root)
    if branch is not None:
        latest_commit = run_command(["git", "log", "-1", "--pretty=%h (%cr): %s"], project_root)
        status_output = run_command(["git", "status", "--porcelain"], project_root)
        status = "[green]Clean[/]" if not status_output else "[bold yellow]Dirty[/] (uncommitted changes)"
        
        console.print(f"  Branch         : [bold yellow]{branch}[/]")
        console.print(f"  Last Commit    : {latest_commit}")
        console.print(f"  Status         : {status}")
    else:
        console.print("  [dim]Not a Git repository.[/dim]")
    
    console.print()