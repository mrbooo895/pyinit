# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'format' command for the pyinit command-line tool.

This module provides a convenient wrapper around standard Python code formatters,
'isort' for sorting imports and 'black' for opinionated code formatting.
It automates the installation of these tools and runs them against the
project's 'src/' and 'tests/' directories to ensure a consistent code style.
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
def format_project():
    """
    Formats the project's codebase using isort and black.

    This function serves as the main entry point for the 'pyinit format' command.
    It performs the following actions:
    1. Verifies the project context and virtual environment.
    2. Checks if 'isort' and 'black' are installed in the venv, installing
       them if necessary.
    3. Sequentially runs 'isort' and then 'black' on the `src/` and `tests/`
       directories if they exist.

    :raises SystemExit: If not run within a valid project, if the virtual
                        environment is not found, or if the installation of
                        the formatters fails.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)

    venv_dir = project_root / "venv"
    check_venv_exists(venv_dir)

    # --- Determine Platform-specific Executables ---
    pip_executable, _ = check_platform(venv_dir)
    _, python_executable = check_platform(venv_dir)

    # --- Ensure Formatters are Installed ---
    # Check if both formatters can be imported.
    check_formatters_cmd = [str(python_executable), "-c", "import black, isort"]
    formatters_installed = (
        subprocess.run(check_formatters_cmd, capture_output=True).returncode == 0
    )

    console.print("[bold green]    Starting[/bold green] to format project's structure")

    if not formatters_installed:
        console.print(
            "[bold green]     Installing[/bold green] Required formatting modules 'black' and 'isort'"
        )
        install_cmd = [str(pip_executable), "install", "black", "isort"]
        try:
            subprocess.run(install_cmd, check=True, capture_output=True)
            console.print(
                "[bold green]      Successfully[/bold green] installed formatting tools."
            )
        except subprocess.CalledProcessError as e:
            console.print(
                "[bold red][ERROR][/bold red] Failed to install formatting tools."
            )
            console.print(f"[red]{e.stderr.decode()}[/red]")
            sys.exit(1)

    # --- Define and Run Formatting on Target Directories ---
    # Default directories to format.
    targets_to_format = [project_root / "src", project_root / "tests"]
    formatted_something = False

    for target_dir in targets_to_format:
        if target_dir.exists() and target_dir.is_dir():
            console.print(
                f"[bold green]     Formatting[/bold green] '{target_dir.relative_to(project_root)}/'"
            )

            # Define commands for isort (sorts imports) and black (formats code).
            # isort should run first.
            isort_cmd = [str(python_executable), "-m", "isort", str(target_dir)]
            black_cmd = [str(python_executable), "-m", "black", str(target_dir)]

            # Run formatters; output is captured to keep the console clean.
            subprocess.run(isort_cmd, capture_output=True)
            subprocess.run(black_cmd, capture_output=True)
            formatted_something = True

    # --- Final User Feedback ---
    if formatted_something:
        console.print("\n[bold green]Successfully[/bold green] Formatted Codebase")
    else:
        # This case occurs if neither 'src/' nor 'tests/' exist.
        console.print(
            "[bold yellow][INFO][/bold yellow] No source 'src' or test 'tests' directories found to format."
        )
