# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'env' command for the pyinit command-line tool.

This module provides functionality for managing project-specific environment
variables stored in a `.env` file. It allows users to easily set variables,
and it automatically ensures that the `.env` file is included in `.gitignore`
to prevent sensitive credentials from being committed to version control.
"""

from pathlib import Path

from rich.console import Console

from .utils import check_project_root, find_project_root
from .wrappers import error_handling


def update_gitignore(project_root: Path, console: Console):
    """
    Ensures that the `.env` file is listed in the project's `.gitignore`.

    This utility function checks if `.gitignore` exists and contains an entry
    for `.env`. If not, it creates the file or appends the entry, providing
    a safeguard against committing sensitive data.

    :param Path project_root: The root directory of the project.
    :param Console console: The rich Console instance for printing messages.
    """
    gitignore_path = project_root / ".gitignore"
    env_entry = "\n# Environment variables\n.env\n"

    # Create .gitignore if it doesn't exist.
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write(env_entry)
        return

    # Append .env entry if it's not already present.
    with open(gitignore_path, "r") as f:
        content = f.read()

    if ".env" not in content:
        with open(gitignore_path, "a") as f:
            f.write(env_entry)


@error_handling
def manage_env(vars_to_set: list):
    """
    Sets one or more environment variables in the project's `.env` file.

    This function serves as the main entry point for the 'pyinit env set' command.
    It reads the existing `.env` file (if any), updates or adds the new
    variables provided by the user, and writes the result back to the file.
    It also calls `update_gitignore` to ensure the file is ignored by Git.

    :param list vars_to_set: A list of strings, each in 'KEY=VALUE' format.
    :raises SystemExit: If not run within a valid project.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)

    # --- Read Existing .env File ---
    # Load existing variables into a dictionary to preserve them.
    env_file_path = project_root / ".env"
    env_vars = {}

    if env_file_path.exists():
        with open(env_file_path, "r") as f:
            for line in f:
                line = line.strip()
                # Ignore comments and empty lines.
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

    # --- Update Variables ---
    # Process the user-provided variables, adding them to or updating the dictionary.
    console.print("[bold green]    Updating[/bold green] '.env' file")

    for var in vars_to_set:
        if "=" not in var:
            console.print(
                f"[bold red][ERROR][/bold red] Invalid format: '{var}'. Expected KEY=VALUE."
            )
            continue
        key, value = var.split("=", 1)
        env_vars[key] = value
        console.print(
            f"[bold green]     Setting[/bold green] [yellow]{key}[/yellow] to [cyan]'{value}'[/cyan]"
        )

    # --- Write Updated .env File ---
    # Overwrite the file with the complete, updated set of variables.
    with open(env_file_path, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    # Ensure the .env file is ignored by version control.
    update_gitignore(project_root, console)

    console.print("\n[bold green]Successfully[/bold green] updated '.env' file.")
