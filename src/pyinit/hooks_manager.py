import sys
import subprocess
import time
from rich.console import Console
from .utils import find_project_root
from .wrappers import error_handling

@error_handling
def add_git_hooks():
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)

    if not (project_root / ".git").is_dir():
        console.print("[bold red][ERROR][/bold red] This is not a Git repository. Please run 'git init' first.")
        sys.exit(1)
        
    venv_dir = project_root / "venv"
    if not venv_dir.exists():
        console.print("[bold red][ERROR][/bold red] Virtual environment 'venv' not found.")
        sys.exit(1)

    if sys.platform == "win32":
        python_executable = venv_dir / "Scripts" / "python.exe"
        pip_executable = venv_dir / "Scripts" / "pip.exe"
        pre_commit_executable = venv_dir / "Scripts" / "pre-commit.exe"
    else:
        python_executable = venv_dir / "bin" / "python"
        pip_executable = venv_dir / "bin" / "pip"
        pre_commit_executable = venv_dir / "bin" / "pre-commit"

    console.print("[bold green]    Checking[/bold green] for 'pre-commit' framework")
    time.sleep(0.25)
    
    check_tool_cmd = [str(python_executable), "-c", "import pre_commit"]
    tool_installed = subprocess.run(check_tool_cmd, capture_output=True).returncode == 0
    
    if not tool_installed:
        console.print("[bold green]     Installing[/bold green] required module 'pre-commit'")
        install_cmd = [str(pip_executable), "install", "pre-commit"]
        try:
            subprocess.run(install_cmd, check=True, capture_output=True)
            console.print("[bold green]    Successfully[/bold green] installed 'pre-commit'")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red][ERROR][/bold red] Failed to install pre-commit: {e.stderr.decode()}")
            sys.exit(1)
            
    config_file_path = project_root / ".pre-commit-config.yaml"
    if config_file_path.exists():
        confirm = console.input("[bold yellow][WARNING][/] a '.pre-commit-config.yaml' already exists. Overwrite? (y/N): ")
        if confirm.lower() != 'y':
            console.print("[bold yellow]Operation cancelled.[/bold yellow]")
            sys.exit(0)

    console.print("[bold green]      Creating[/bold green] default pre-commit configuration")
    time.sleep(0.25)

    config_content = """\
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
    -   id: ruff
        args: [--fix, --exit-non-zero-on-fix]
    -   id: ruff-format

-   repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
    -   id: black

-   repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
    -   id: isort
        name: isort (python)
"""

    with open(config_file_path, "w") as f:
        f.write(config_content)
    
    console.print("[bold green]       Installing[/bold green] git hooks into '.git/' directory")
    time.sleep(0.25)
    
    try:
        install_hooks_cmd = [str(pre_commit_executable), "install"]
        subprocess.run(install_hooks_cmd, cwd=project_root, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red][ERROR][/bold red] Failed to install git hooks: {e.stderr.decode()}")
        sys.exit(1)

    console.print("\n[bold green]Successfully[/bold green] set up pre-commit hooks.\n")
    console.print("[bold green]->[/] Hooks will now run automatically on 'git commit'.")