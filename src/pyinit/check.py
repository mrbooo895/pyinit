# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'check' command for the pyinit command-line tool.

This module provides a convenient wrapper around the 'ruff' linter. It handles
the automatic installation of ruff if not present, and by default, it runs
the linter against the standard 'src/' and 'tests/' directories. It also
allows users to pass additional arguments directly to ruff for more advanced usage.
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
def check_project(check_args: list = None):
    """
    Checks the project's codebase using the ruff linter.

    This function serves as the main entry point for the 'pyinit check' command.
    It ensures ruff is installed in the virtual environment and then executes it.
    If no specific paths or arguments are provided by the user, it defaults to
    linting the `src/` and `tests/` directories.

    :param list, optional Check_args: A list of arguments to be passed directly
                                     to the 'ruff check' command. Defaults to None.
    :raises SystemExit: If the command is not run within a valid project,
                        if the virtual environment is not found, or if the
                        installation of ruff fails.
    """
    console = Console()
    project_root = find_project_root()
    if not check_args:
        check_args = []

    # --- Pre-flight Checks ---
    check_project_root(project_root)

    venv_dir = project_root / "venv"
    check_venv_exists(venv_dir)

    # --- Determine Platform-specific Executables ---
    pip_executable, _ = check_platform(venv_dir)
    _, python_executable = check_platform(venv_dir)

    # --- Ensure Linter is Installed ---
    console.print("[bold green]    Checking[/bold green] for linter 'ruff'")

    # A simple way to check for a package without parsing `pip list`.
    check_linter_cmd = [str(python_executable), "-c", "import ruff"]
    linter_installed = (
        subprocess.run(check_linter_cmd, capture_output=True).returncode == 0
    )

    if not linter_installed:
        console.print(
            "[bold green]     Installing[/bold green] Required Checking Module 'ruff'"
        )
        install_cmd = [str(pip_executable), "install", "ruff"]
        try:
            subprocess.run(install_cmd, check=True, capture_output=True)
            console.print(
                "[bold green]      Successfully[/bold green] installed 'ruff'"
            )
        except subprocess.CalledProcessError as e:
            console.print("[bold red][ERROR][/bold red] Failed to install ruff.")
            console.print(f"[red]{e.stderr.decode()}[/red]")
            sys.exit(1)
    else:
        console.print("[bold green]     Found[/bold green] Linting Module 'ruff'")

    # --- Prepare and Run Linter Command ---
    # Base command to execute ruff.
    lint_cmd = [str(python_executable), "-m", "ruff", "check"] + check_args

    # If no arguments were passed, use default target directories.
    # This prevents ruff from running on the entire project root by default.
    if not check_args:
        targets = []
        src_dir = project_root / "src"
        tests_dir = project_root / "tests"
        if src_dir.exists():
            targets.append(str(src_dir))
        if tests_dir.exists():
            targets.append(str(tests_dir))

        if not targets:
            console.print(
                "[bold yellow][INFO][/bold yellow] No source ('src') or test ('tests') directories found to lint."
            )
            sys.exit(0)

        lint_cmd.extend(targets)

    console.print("[bold green]\nRunning[/bold green] Checks on codebase\n")

    # Run the linter. Output is streamed directly to the console.
    subprocess.run(lint_cmd)

    console.print("\n[bold green]Checking[/bold green] process completed.")
