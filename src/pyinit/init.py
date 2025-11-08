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
import venv
from pathlib import Path

from rich.console import Console

from .create import TEMPLATE_PATH, get_git_config
from .wrappers import error_handling


def sanitize_name(name: str) -> str:
    """
    Cleans a string to make it a valid Python package name.

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

    This function performs the following:
    1. Derives and sanitizes a project name from the current directory name.
    2. Performs safety checks to prevent overwriting an existing project.
    3. Manually creates the standard project structure (`src/`, `tests/`, etc.).
    4. Generates `pyproject.toml` from a system-wide template.
    5. Migrates any existing `.py` files from the root into the new source directory.
    6. Initializes a Git repository and a virtual environment.

    :raises SystemExit: If the directory appears to be an existing project or
                        if any step in the process fails.
    """
    console = Console()
    project_root = Path.cwd()

    console.print(
        f"[bold green]    Initializing[/bold green] project in '{project_root.name}'"
    )

    # --- Pre-flight Checks ---
    original_name = project_root.name
    project_name = sanitize_name(original_name)
    if not project_name:
        console.print(
            f"[bold red][ERROR][/bold red] Could not derive a valid project name from '{original_name}'"
        )
        sys.exit(1)

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
    python_files_to_move = [
        f for f in project_root.iterdir() if f.is_file() and f.suffix == ".py"
    ]
    has_main_py = any(f.name == "main.py" for f in python_files_to_move)

    temp_migration_dir = project_root / "__pyinit_migration_temp__"
    if python_files_to_move:
        temp_migration_dir.mkdir()
        for py_file in python_files_to_move:
            shutil.move(py_file, temp_migration_dir / py_file.name)

    try:
        # --- Create Directory Structure ---
        source_dir = project_root / "src" / project_name
        tests_dir = project_root / "tests"
        source_dir.mkdir(parents=True)
        tests_dir.mkdir()
        (source_dir / "__init__.py").touch()
        (tests_dir / "__init__.py").touch()
        (project_root / "README.md").write_text(f"# {project_name}\n")

        # --- Safe File Migration (Phase 2) ---
        if python_files_to_move:
            for py_file in temp_migration_dir.iterdir():
                shutil.move(py_file, source_dir / py_file.name)
            temp_migration_dir.rmdir()

        # Create a default main.py only if one was not migrated.
        if not has_main_py:
            (source_dir / "main.py").write_text(
                f'print("Hello from {project_name}!")\n'
            )

        # --- Generate pyproject.toml ---
        try:
            template_content = TEMPLATE_PATH.read_text(encoding="utf-8")
        except FileNotFoundError:
            console.print(
                f"[bold red][ERROR][/bold red] Template file not found at '{TEMPLATE_PATH}'."
            )
            console.print("[dim]       - Ensure pyinit is installed correctly.[/dim]")
            sys.exit(1)

        author_name = get_git_config("user.name") or "Your Name"
        author_email = get_git_config("user.email") or "you@example.com"

        pyproject_content = template_content.replace("##PROJECT_NAME##", project_name)
        pyproject_content = pyproject_content.replace("##AUTHOR_NAME##", author_name)
        pyproject_content = pyproject_content.replace("##AUTHOR_EMAIL##", author_email)

        (project_root / "pyproject.toml").write_text(pyproject_content)

        # --- Finalization ---
        if not (project_root / ".git").exists():
            subprocess.run(
                ["git", "init"], cwd=project_root, check=True, capture_output=True
            )

        venv.create(project_root / "venv", with_pip=True)

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

        console.print(
            f"\n[bold green]Successfully[/bold green] initialized project '{project_name}'"
        )

    except Exception as e:
        # --- Rollback on Failure ---
        console.print(f"[bold red][ERROR][/bold red] Failed during initialization: {e}")
        if temp_migration_dir.exists():
            for py_file in temp_migration_dir.iterdir():
                shutil.move(py_file, project_root / py_file.name)
            temp_migration_dir.rmdir()
        sys.exit(1)
