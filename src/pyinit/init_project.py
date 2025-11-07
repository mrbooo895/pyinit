import os
import sys
import re
import shutil
import venv
import subprocess
import time
from pathlib import Path
from rich.console import Console
from .new_project import get_git_config
from .wrappers import error_handling

def sanitize_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r'[\s-]', '_', name)
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name

@error_handling
def initialize_project():
    console = Console()
    project_root = Path.cwd()

    console.print(f"[bold green]    Initializing[/bold green] existing project")
    time.sleep(0.5)

    original_name = project_root.name
    project_name = sanitize_name(original_name)
    if not project_name:
        console.print(f"[bold red][ERROR][/bold red] Could not derive a valid project name from '{original_name}'")
        sys.exit(1)

    console.print(f"[bold green]     Setting[/bold green] Project Name to: '{project_name}'")
    time.sleep(0.5)

    if (project_root / "pyproject.toml").exists():
        console.print("[bold red][ERROR][/bold red] a 'pyproject.toml' file already exists. Aborting.")
        sys.exit(1)

    if (project_root / "src").exists():
        console.print("[bold red][ERROR][/bold red] a 'src' directory already exists. Please remove or rename it first.")
        sys.exit(1)
    
    if (project_root / "venv").exists():
        console.print("[bold red][ERROR][/bold red] a 'venv' directory already exists. Aborting.")
        sys.exit(1)

    console.print(f"[bold green]      Creating[/bold green] Project Structure")
    time.sleep(0.5)
    source_dir = project_root / "src" / project_name
    os.makedirs(source_dir)

    console.print(f"[bold green]      Locating[/bold green] '.py' files to migrate")
    time.sleep(0.5)
    python_files_to_move = [f for f in project_root.iterdir() if f.is_file() and f.suffix == ".py"]

    if python_files_to_move:
        for py_file in python_files_to_move:
            try:
                shutil.move(py_file, source_dir)
            except Exception as e:
                console.print(f"[bold red][ERROR][/bold red] Could not move '{py_file.name}': {e}")
                sys.exit(1)
    
    if not (source_dir / "main.py").exists():
        with open(source_dir / "main.py", "w") as file:
            file.write('print("Hello World!")\n')

    console.print(f"[bold green]       Creating[/bold green] configuration files")
    time.sleep(0.5)

    gitignore_content = """# Virtual Environment
venv/
__pycache__/
*.pyc

# Build artifacts
dist/
build/
*.egg-info/

# IDE Specific Files
.idea/
.vscode/
"""
    with open(project_root / ".gitignore", "w") as file:
        file.write(gitignore_content.strip())

    pyproject_template_path = "/usr/share/pyinit/pyprojinit.toml"
    try:
        with open(pyproject_template_path, "r") as template_file:
            template = template_file.read()

        author_name = get_git_config("user.name") or "Your Name"
        author_email = get_git_config("user.email") or "you@example.com"

        content = template.replace("##PROJECT_NAME##", project_name)
        content = content.replace("##AUTHOR_NAME##", author_name)
        content = content.replace("##AUTHOR_EMAIL##", author_email)

        with open(project_root / "pyproject.toml", "w") as project_file:
            project_file.write(content)
    except FileNotFoundError:
        console.print(f"[bold red][ERROR][/bold red] Template file not found at '{pyproject_template_path}'")
        sys.exit(1)

    console.print(f"[bold green]    Finalizing[/bold green] setup")
    time.sleep(0.5)
    if not (project_root / ".git").exists():
        subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
    
    venv.create(project_root / "venv", with_pip=True)

    console.print(f"[bold green]\nSuccessfully[/bold green] initialized project '{project_name}'")