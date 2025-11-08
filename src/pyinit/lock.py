# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'lock' command for the pyinit command-line tool.

This module is responsible for generating a `requirements.txt` file, which
"locks" the current state of the project's dependencies to specific versions.
This is a crucial practice for creating reproducible environments.
"""

import subprocess
import sys

from rich.console import Console

from .utils import (
    check_platform,
    check_project_root,
    check_venv_exists,
    find_project_root,
)
from .wrappers import error_handling


@error_handling
def lock_dependencies():
    """
    Generates a `requirements.txt` file from the project's virtual environment.

    This function serves as the main entry point for the 'pyinit lock' command.
    It uses the `pip freeze` command within the project's virtual environment
    to capture a list of all installed packages and their exact versions,
    then writes this list to `requirements.txt` in the project root.

    :raises SystemExit: If not run within a valid project, if the virtual
                        environment is not found, or if the `pip freeze`
                        command fails.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)

    venv_dir = project_root / "venv"
    check_venv_exists(venv_dir)

    requirements_file = project_root / "requirements.txt"

    # --- Determine Platform-specific Executables ---
    pip_executable, _ = check_platform(venv_dir)

    # --- Dependency Freezing Process ---
    console.print(
        f"[bold green]    Locking[/bold green] dependencies to '{requirements_file.name}'"
    )

    # The command to be executed to get the list of installed packages.
    freeze_cmd = [str(pip_executable), "freeze"]

    try:
        # Execute `pip freeze` and capture its standard output.
        result = subprocess.run(freeze_cmd, check=True, capture_output=True, text=True)

        # Write the captured output directly to requirements.txt, overwriting
        # any existing file content.
        with open(requirements_file, "w") as f:
            f.write(result.stdout)

        console.print(
            f"[bold green]Successfully[/bold green] created '{requirements_file.name}'."
        )

    except subprocess.CalledProcessError as e:
        # Handle cases where the `pip freeze` command itself fails.
        console.print("[bold red][ERROR][/bold red] Failed to run 'pip freeze'.")
        console.print(f"[red]{e.stderr}[/red]")
        sys.exit(1)
    except Exception as e:
        # Catch other potential issues, such as file writing errors.
        console.print(f"[bold red][ERROR][/bold red] An unexpected error occurred: {e}")
        sys.exit(1)
