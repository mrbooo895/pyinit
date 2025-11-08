# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'clean' command for the pyinit command-line tool.

This module is responsible for removing temporary files and build artifacts
from a project directory. It helps in maintaining a clean workspace by
deleting cached files, test artifacts, and distribution packages.
"""

import shutil
import sys
import time
from pathlib import Path

from rich.console import Console

from .utils import find_project_root
from .wrappers import error_handling


@error_handling
def clean_project():
    """
    Removes temporary and build-related files from the current project.

    This function serves as the entry point for the 'pyinit clean' command.
    It recursively searches for a predefined list of patterns (like `__pycache__`,
    `dist/`, etc.), prompts the user for confirmation before deleting, and then
    removes the identified files and directories.

    :raises SystemExit: If not run within a valid project or if the user
                        cancels the operation.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    if not project_root:
        console.print(
            "[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'."
        )
        sys.exit(1)

    # A list of glob patterns for files and directories to be removed.
    patterns_to_remove = [
        "__pycache__",
        ".pytest_cache",
        "build",
        "dist",
        "*.egg-info",
        ".coverage",
    ]

    # --- Search Phase ---
    # Recursively search the project directory for all items matching the patterns.
    console.print(
        "[bold green]    Searching[/bold green] for temporary and build-related files"
    )
    time.sleep(0.25)

    paths_to_remove: list[Path] = []
    for pattern in patterns_to_remove:
        paths_to_remove.extend(project_root.rglob(pattern))

    if not paths_to_remove:
        console.print(
            "[bold yellow][INFO][/bold yellow] Project is already clean. Nothing to remove."
        )
        sys.exit(0)

    # --- Confirmation Phase ---
    # Display the found items and ask for user confirmation before deletion.
    console.print(
        "[bold yellow][INFO][/bold yellow] The following files and directories will be permanently removed:"
    )
    for path in paths_to_remove:
        relative_path = path.relative_to(project_root)
        console.print(f"  - {relative_path}")

    try:
        confirm = console.input("\n - Are you sure you want to proceed? (y/N): ")
        if confirm.lower() != "y":
            console.print(
                "[bold yellow][INFO][/bold yellow] Operation cancelled by user."
            )
            sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        # Handle cases where the user interrupts the input prompt (e.g., Ctrl+C).
        console.print(
            "\n[bold yellow][WARNING][/bold yellow] Operation cancelled by user."
        )
        sys.exit(0)

    # --- Deletion Phase ---
    # Proceed with removing the files and directories.
    console.print("[bold green]\n     Cleaning[/bold green] project...")
    time.sleep(0.25)

    deleted_count = 0
    for path in paths_to_remove:
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            deleted_count += 1
        except OSError as e:
            # Report any errors during deletion but continue with other files.
            console.print(f"[bold red][ERROR][/bold red] Could not remove {path}: {e}")

    console.print(
        f"\n[bold green]Successfully[/bold green] removed {deleted_count} items."
    )
