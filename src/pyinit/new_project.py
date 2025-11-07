import os
import subprocess
import venv
import time
import sys
import shutil
from pathlib import Path
from rich.console import Console
from .wrappers import error_handling

TEMPLATES_BASE_DIR = Path("/usr/share/pyinit/templates")

def get_git_config(key):
    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True, check=True, text=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def copy_and_process_template(template_path: Path, dest_path: Path, replacements: dict):
    for item in template_path.rglob('*'):
        relative_path = item.relative_to(template_path)
        
        processed_relative_path_str = str(relative_path)
        for placeholder, value in replacements.items():
            processed_relative_path_str = processed_relative_path_str.replace(placeholder, value)

        dest_item_path = dest_path / processed_relative_path_str
        
        if item.is_dir():
            dest_item_path.mkdir(parents=True, exist_ok=True)
        else:
            with open(item, "r", encoding="utf-8") as src_file:
                content = src_file.read()
            
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            
            with open(dest_item_path, "w", encoding="utf-8") as dest_file:
                dest_file.write(content)

@error_handling
def create_project(project_path, template_name):
    console = Console()
    project_name = Path(project_path).name

    console.print(f"[bold green]    Creating[/bold green] project '{project_name}' from template '{template_name}'")
    time.sleep(0.25)
    
    project_root = Path.cwd() / project_path
    template_dir = TEMPLATES_BASE_DIR / template_name

    if not template_dir.is_dir():
        console.print(f"[bold red][ERROR][/bold red] Template '{template_name}' not found at '{TEMPLATES_BASE_DIR}'.")
        sys.exit(1)

    if project_root.exists():
        console.print(f"[bold red][ERROR][/bold red] Folder '{project_path}' already exists.")
        sys.exit(1)

    try:
        project_root.mkdir()
        author_name = get_git_config("user.name") or "Your Name"
        author_email = get_git_config("user.email") or "you@example.com"

        replacements = {
            "##PROJECT_NAME##": project_name,
            "##AUTHOR_NAME##": author_name,
            "##AUTHOR_EMAIL##": author_email,
        }
        
        copy_and_process_template(template_dir, project_root, replacements)
        venv.create(project_root / "venv", with_pip=True)
        subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
        
        gitignore_path = project_root / ".gitignore"
        gitignore_content = """\n# Virtual Environment
venv/
__pycache__/
*.pyc

# IDE Specific Files
.idea/
.vscode/

# Build artifacts
dist/
build/
*.egg-info/
"""
        with open(gitignore_path, "a") as f: 
            f.write(gitignore_content)
        
        console.print(f"[bold green]Successfully[/bold green] created project '{project_name}'.")
        console.print(f"[bold green]note[/]: see more informations and configuration in 'pyproject.toml'")
    
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] Failed to create project: {e}")
        if project_root.exists():
            shutil.rmtree(project_root)
        sys.exit(1)