# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'create' command for the pyinit command-line tool.

This module is the core of project scaffolding. It creates a new, standardized,
and fully structured Python project. It handles directory creation, configuration
file generation, virtual environment setup, and Git repository initialization.
"""

import shutil
import subprocess
import sys
import venv
from pathlib import Path

# Use importlib.resources to access package data in a cross-platform way.
# This avoids hardcoded paths like /usr/share.
try:
    from importlib.resources import files as resources_files
except ImportError:
    # Fallback for Python < 3.9
    from importlib_resources import files as resources_files

from rich.console import Console

from .wrappers import error_handling


def get_git_config(key: str) -> str | None:
    """
    Retrieves a specified configuration value from the global Git config.

    Used to fetch user details like name and email to pre-fill project metadata.

    :param str key: The Git configuration key to retrieve (e.g., 'user.name').
    :return: The configured value, or None if not found or Git is not installed.
    :rtype: str or None
    """
    try:
        result = subprocess.run(
            ["git", "config", "--get", key], capture_output=True, check=True, text=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


@error_handling
def create_project(project_path: str):
    """
    Creates a new, standardized Python project structure.

    This is the main entry point for the 'pyinit create' command. It orchestrates
    the entire project creation process, including directory creation, generation
    of configuration files from an internal template, and initialization of
    Git and a virtual environment.

    :param str project_path: The path/name for the new project directory.
    :raises SystemExit: If the destination directory already exists or if
                        any part of the creation process fails.
    """
    console = Console()
    project_name = Path(project_path).name

    console.print(f"[bold green]    Creating[/bold green] project '{project_name}'")

    project_root = Path.cwd() / project_path

    # --- Pre-flight Checks ---
    if project_root.exists():
        console.print(f"[bold red][ERROR][/bold red] Folder '{project_path}' already exists.")
        sys.exit(1)

    try:
        # --- Create Directory Structure ---
        source_dir = project_root / "src" / project_name
        tests_dir = project_root / "tests"
        source_dir.mkdir(parents=True)
        tests_dir.mkdir()
        (source_dir / "__init__.py").touch()
        (source_dir / "main.py").write_text(f'print("Hello from {project_name}!")\n')
        (tests_dir / "__init__.py").touch()
        (project_root / "README.md").write_text(f"# {project_name}\n")


        # --- Generate pyproject.toml ---
        # Access the template file packaged with the tool itself.
        template_ref = resources_files("pyinit._templates").joinpath("pyproject.toml")
        template_content = template_ref.read_text(encoding="utf-8")
        
        author_name = get_git_config("user.name") or "Your Name"
        author_email = get_git_config("user.email") or "you@example.com"

        # Replace placeholders in the template content.
        pyproject_content = template_content.replace("##PROJECT_NAME##", project_name)
        pyproject_content = pyproject_content.replace("##AUTHOR_NAME##", author_name)
        pyproject_content = pyproject_content.replace("##AUTHOR_EMAIL##", author_email)

        (project_root / "pyproject.toml").write_text(pyproject_content)

        # --- Environment Initialization ---
        venv.create(project_root / "venv", with_pip=True)
        subprocess.run(
            ["git", "init"], cwd=project_root, check=True, capture_output=True
        )

        # --- Create .gitignore ---
        gitignore_content = """# Virtual Environment
venv/
.venv/
__pycache__/

# Build artifacts
dist/
build/
*.egg-info/

# IDE & OS files
.idea/
.vscode/
.DS_Store

# Test artifacts
.pytest_cache/
.coverage
"""
        (project_root / ".gitignore").write_text(gitignore_content.strip())
        
        console.print(f"[bold green]Successfully[/bold green] created project '{project_name}'.")

    except Exception as e:
        # --- Rollback on Failure ---
        console.print(f"[bold red][ERROR][/bold red] Failed to create project: {e}")
        if project_root.exists():
            shutil.rmtree(project_root)
        sys.exit(1)