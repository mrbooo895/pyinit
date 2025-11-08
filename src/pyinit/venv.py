# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'venv' command group for the pyinit command-line tool.

This module provides sub-commands for explicit management of the project's
virtual environment, allowing users to create or remove it on demand.
This offers more control over the project's state.
"""

import shutil
import sys
import time
import venv
from pathlib import Path

from rich.console import Console

from .utils import find_project_root
from .wrappers import error_handling


@error_handling
def manage_venv(action: str):
    """
    Main dispatcher for 'venv' sub-commands.

    This function serves as the entry point for 'pyinit venv'. It validates
    the project context and then routes to the appropriate handler function
    (`create_virtual_env` or `remove_virtual_env`) based on the user's
    chosen action.

    :param str action: The sub-command to execute ('create' or 'remove').
    :raises SystemExit: If not run within a valid project.
    """
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print(
            "[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'."
        )
        sys.exit(1)

    venv_dir = project_root / "venv"

    # Route to the specific function based on the sub-command.
    if action == "create":
        create_virtual_env(console, venv_dir)
    elif action == "remove":
        remove_virtual_env(console, venv_dir)


def create_virtual_env(console: Console, venv_dir: Path):
    """
    Creates a new virtual environment for the project.

    Handles the logic for the 'pyinit venv create' command. It includes a
    safety check to prevent overwriting an existing environment.

    :param Console console: The rich Console instance for output.
    :param Path venv_dir: The path where the virtual environment should be created.
    :raises SystemExit: If a virtual environment already exists or if creation fails.
    """
    console.print("[bold green]     Creating[/bold green] virtual environment")
    time.sleep(0.25)

    if venv_dir.exists():
        console.print("[bold red][ERROR][/bold red] A 'venv' directory already exists.")
        console.print(
            "       - If you want to recreate it, run 'pyinit venv remove' first."
        )
        sys.exit(1)

    try:
        # Use Python's built-in venv module to create the environment.
        venv.create(venv_dir, with_pip=True)
        console.print(
            "\n[bold green]Successfully[/bold green] created virtual environment."
        )
    except Exception as e:
        console.print(
            f"[bold red][ERROR][/bold red] Failed to create virtual environment: {e}"
        )
        sys.exit(1)


def remove_virtual_env(console: Console, venv_dir: Path):
    """
    Removes the project's existing virtual environment.

    Handles the logic for the 'pyinit venv remove' command. As this is a
    destructive action, it includes a critical confirmation prompt before
    proceeding with the deletion of the 'venv' directory.

    :param Console console: The rich Console instance for output and input.
    :param Path venv_dir: The path of the virtual environment to be removed.
    :raises SystemExit: If the environment does not exist, if the user cancels,
                        or if removal fails.
    """
    console.print("[bold yellow]     Removing[/bold yellow] virtual environment")
    time.sleep(0.25)

    if not venv_dir.exists() or not venv_dir.is_dir():
        console.print(
            "[bold yellow][INFO][/bold yellow] No 'venv' directory found to remove."
        )
        sys.exit(1)

    try:
        # Prompt the user for confirmation due to the destructive nature of the action.
        confirm = console.input(
            "[bold red][CRITICAL][/bold red] This is a destructive action. Are you sure you want to remove the entire 'venv' directory? (y/N): "
        )
        if confirm.lower() == "y":
            console.print(
                f"[bold green]      Deleting[/bold green] directory '{venv_dir.name}'"
            )
            time.sleep(0.25)
            # Recursively delete the directory and all its contents.
            shutil.rmtree(venv_dir)
            console.print(
                "\n[bold green]Successfully[/bold green] removed virtual environment."
            )
        else:
            console.print(
                "[bold yellow][INFO][/bold yellow] Operation cancelled by user."
            )
            sys.exit(0)
    except Exception as e:
        console.print(
            f"[bold red][ERROR][/bold red] Failed to remove virtual environment: {e}"
        )
        sys.exit(1)
