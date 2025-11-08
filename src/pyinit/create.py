# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'new' command for the pyinit command-line tool.

This module is the core of project scaffolding. It creates a new, fully
structured Python project from a predefined template. It handles directory
creation, template file processing, virtual environment setup, and Git
repository initialization.
"""

import shutil
import subprocess
import sys
import venv
from pathlib import Path

from rich.console import Console

from .wrappers import error_handling

# Define the base directory where all project templates are stored.
TEMPLATES_BASE_DIR = Path("/usr/share/pyinit/templates")


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


def process_template(template_path: Path, dest_path: Path, replacements: dict):
    """
    Recursively copies a template directory, processing file contents and names.

    This function walks through the template directory. For each file and folder,
    it replaces placeholder strings (like '##PROJECT_NAME##') in both the content
    and the file/folder name itself before writing it to the destination.

    :param Path template_path: The source directory of the template.
    :param Path dest_path: The root directory where the project will be created.
    :param dict replacements: A dictionary of placeholder strings to their
                              replacement values.
    """
    for item in template_path.rglob("*"):
        relative_path = item.relative_to(template_path)

        # Process placeholders in the path itself (e.g., 'src/##PROJECT_NAME##').
        processed_relative_path_str = str(relative_path)
        for placeholder, value in replacements.items():
            processed_relative_path_str = processed_relative_path_str.replace(
                placeholder, value
            )

        dest_item_path = dest_path / processed_relative_path_str

        if item.is_dir():
            dest_item_path.mkdir(parents=True, exist_ok=True)
        else:
            # Read, process, and write file content.
            with open(item, "r", encoding="utf-8") as src_file:
                content = src_file.read()

            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)

            with open(dest_item_path, "w", encoding="utf-8") as dest_file:
                dest_file.write(content)


@error_handling
def create_project(project_path: str, template_name: str):
    """
    Creates a new, structured Python project from a specified template.

    This is the main entry point for the 'pyinit new' command. It orchestrates
    the entire project creation process, including validating inputs, processing
    the template, and initializing Git and a virtual environment.

    :param str project_path: The path/name for the new project directory.
    :param str template_name: The name of the template to use.
    :raises SystemExit: If the specified template is not found, if the
                        destination directory already exists, or if any
                        part of the creation process fails.
    """
    console = Console()
    project_name = Path(project_path).name

    console.print(
        f"[bold green]    Creating[/bold green] project '{project_name}' from template '{template_name}'"
    )

    project_root = Path.cwd() / project_path
    template_dir = TEMPLATES_BASE_DIR / template_name

    # --- Pre-flight Checks ---
    if not template_dir.is_dir():
        console.print(
            f"[bold red][ERROR][/bold red] Template '{template_name}' not found at '{TEMPLATES_BASE_DIR}'."
        )
        sys.exit(1)

    if project_root.exists():
        console.print(
            f"[bold red][ERROR][/bold red] Folder '{project_path}' already exists."
        )
        sys.exit(1)

    try:
        # --- Project Scaffolding ---
        project_root.mkdir()
        author_name = get_git_config("user.name") or "Your Name"
        author_email = get_git_config("user.email") or "you@example.com"

        replacements = {
            "##PROJECT_NAME##": project_name,
            "##AUTHOR_NAME##": author_name,
            "##AUTHOR_EMAIL##": author_email,
        }

        process_template(template_dir, project_root, replacements)

        # --- Environment Initialization ---
        venv.create(project_root / "venv", with_pip=True)
        subprocess.run(
            ["git", "init"], cwd=project_root, check=True, capture_output=True
        )

        # --- Final Configuration ---
        # Append standard pyinit ignores to .gitignore.
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

        console.print(
            f"[bold green]Successfully[/bold green] created project '{project_name}'."
        )

    except Exception as e:
        # --- Rollback on Failure ---
        # If anything goes wrong, delete the partially created project directory.
        console.print(f"[bold red][ERROR][/bold red] Failed to create project: {e}")
        if project_root.exists():
            shutil.rmtree(project_root)
        sys.exit(1)
