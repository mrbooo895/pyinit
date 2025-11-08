# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'init' command for the pyinit command-line tool.

This module is responsible for transforming an existing directory of Python
scripts into a standardized, structured pyinit project. It creates the
necessary configuration files, directory layout, and migrates existing scripts
into the new source directory.
"""

import re
import shutil
import subprocess
import sys
import time
import venv
from pathlib import Path

from rich.console import Console

# Import shared functionality from the 'new' module.
from .new import TEMPLATES_BASE_DIR, get_git_config, process_template
from .wrappers import error_handling


def sanitize_name(name: str) -> str:
    """
    Cleans a string to make it a valid Python package name.

    Converts to lowercase, replaces spaces and hyphens with underscores,
    and removes any other non-alphanumeric characters.

    :param str name: The original directory or project name.
    :return: A sanitized string suitable for use as a package name.
    :rtype: str
    """
    name = name.lower()
    name = re.sub(r"[\s-]", "_", name)
    name = re.sub(r"[^a-z0-9_]", "", name)
    return name


@error_handling
def initialize_project():
    """
    Initializes a structured project in the current working directory.

    This function serves as the entry point for the 'pyinit init' command. It performs:
    1. Derives and sanitizes a project name from the current directory name.
    2. Performs safety checks to prevent overwriting an existing project.
    3. Safely migrates existing `.py` files from the root to a temporary location.
    4. Scaffolds a new project structure using the default 'app' template.
    5. Moves the migrated Python files into the new `src/<package_name>/` directory.
    6. Initializes a Git repository and a virtual environment.

    :raises SystemExit: If the directory appears to be an existing project or
                        if any step in the process fails.
    """
    console = Console()
    project_root = Path.cwd()
    template_name = "app"  # 'init' command always uses the default 'app' template.
    template_dir = TEMPLATES_BASE_DIR / template_name

    console.print(
        f"[bold green]    Initializing[/bold green] project in '{project_root.name}' using '{template_name}' template"
    )
    time.sleep(0.5)

    # --- Pre-flight Checks ---
    if not template_dir.is_dir():
        console.print(
            f"[bold red][ERROR][/bold red] Default template '{template_name}' not found at '{TEMPLATES_BASE_DIR}'."
        )
        sys.exit(1)

    original_name = project_root.name
    project_name = sanitize_name(original_name)
    if not project_name:
        console.print(
            f"[bold red][ERROR][/bold red] Could not derive a valid project name from '{original_name}'"
        )
        sys.exit(1)

    console.print(
        f"[bold green]     Setting[/bold green] Project Name to: '{project_name}'"
    )
    time.sleep(0.5)

    # Prevent running on an already initialized or structured directory.
    if (
        (project_root / "pyproject.toml").exists()
        or (project_root / "src").exists()
        or (project_root / "venv").exists()
    ):
        console.print(
            "[bold red][ERROR][/bold red] Project already seems to be initialized ('pyproject.toml', 'src', or 'venv' exists)."
        )
        sys.exit(1)

    # --- Safe File Migration (Phase 1) ---
    # Temporarily move existing .py files to prevent conflicts during templating.
    console.print("[bold green]      Locating[/bold green] '.py' files to migrate...")
    time.sleep(0.5)
    python_files_to_move = [
        f for f in project_root.iterdir() if f.is_file() and f.suffix == ".py"
    ]

    temp_migration_dir = project_root / "__pyinit_migration_temp__"
    if python_files_to_move:
        temp_migration_dir.mkdir()
        for py_file in python_files_to_move:
            shutil.move(py_file, temp_migration_dir / py_file.name)

    try:
        # --- Scaffolding from Template ---
        console.print(
            "[bold green]      Creating[/bold green] project structure from template..."
        )
        time.sleep(0.5)

        author_name = get_git_config("user.name") or "Your Name"
        author_email = get_git_config("user.email") or "you@example.com"

        replacements = {
            "##PROJECT_NAME##": project_name,
            "##AUTHOR_NAME##": author_name,
            "##AUTHOR_EMAIL##": author_email,
        }

        # Use the shared templating function from the 'new' module.
        process_template(template_dir, project_root, replacements)

        # --- Safe File Migration (Phase 2) ---
        # Move the temporarily stored files into the new source directory.
        if python_files_to_move:
            console.print(
                "[bold green]   Migrating[/bold green] existing Python files..."
            )
            time.sleep(0.5)
            source_package_dir = project_root / "src" / project_name
            # Remove the default main.py from the template to avoid conflicts.
            (source_package_dir / "main.py").unlink(missing_ok=True)
            for py_file in temp_migration_dir.iterdir():
                shutil.move(py_file, source_package_dir / py_file.name)
            temp_migration_dir.rmdir()

        # --- Finalization ---
        # Initialize Git, create venv, and update .gitignore.
        console.print("[bold green]    Finalizing[/bold green] setup...")
        time.sleep(0.5)

        if not (project_root / ".git").exists():
            subprocess.run(
                ["git", "init"], cwd=project_root, check=True, capture_output=True
            )

        venv.create(project_root / "venv", with_pip=True)

        gitignore_path = project_root / ".gitignore"
        gitignore_content = """\n# Virtual Environment
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
        with open(gitignore_path, "a") as f:
            f.write(gitignore_content)

        console.print(
            f"[bold green]\nSuccessfully[/bold green] initialized project '{project_name}'"
        )

    except Exception as e:
        # --- Rollback on Failure ---
        # If any part of the process fails, attempt to restore the original files.
        console.print(f"[bold red][ERROR][/bold red] Failed during initialization: {e}")
        if temp_migration_dir.exists():
            for py_file in temp_migration_dir.iterdir():
                shutil.move(py_file, project_root / py_file.name)
            temp_migration_dir.rmdir()
        sys.exit(1)
