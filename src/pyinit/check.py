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
import time

from rich.console import Console

from .utils import find_project_root
from .wrappers import error_handling


@error_handling
def lint_project(lint_args: list = None):
    """
    Checks the project's codebase using the ruff linter.

    This function serves as the main entry point for the 'pyinit check' command.
    It ensures ruff is installed in the virtual environment and then executes it.
    If no specific paths or arguments are provided by the user, it defaults to
    linting the `src/` and `tests/` directories.

    :param list, optional lint_args: A list of arguments to be passed directly
                                     to the 'ruff check' command. Defaults to None.
    :raises SystemExit: If the command is not run within a valid project,
                        if the virtual environment is not found, or if the
                        installation of ruff fails.
    """
    console = Console()
    project_root = find_project_root()
    if not lint_args:
        lint_args = []

    # --- Pre-flight Checks ---
    if not project_root:
        console.print(
            "[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'."
        )
        sys.exit(1)

    venv_dir = project_root / "venv"
    if not venv_dir.exists():
        console.print(
            "[bold red][ERROR][/bold red] Virtual environment 'venv' not found."
        )
        sys.exit(1)

    # --- Determine Platform-specific Executables ---
    if sys.platform == "win32":
        python_executable = venv_dir / "Scripts" / "python.exe"
        pip_executable = venv_dir / "Scripts" / "pip.exe"
    else:
        python_executable = venv_dir / "bin" / "python"
        pip_executable = venv_dir / "bin" / "pip"

    # --- Ensure Linter is Installed ---
    console.print("[bold green]    Checking[/bold green] for linter 'ruff'")
    time.sleep(0.25)

    # A simple way to check for a package without parsing `pip list`.
    check_linter_cmd = [str(python_executable), "-c", "import ruff"]
    linter_installed = (
        subprocess.run(check_linter_cmd, capture_output=True).returncode == 0
    )

    if not linter_installed:
        console.print(
            "[bold green]     Installing[/bold green] Required Linting Module 'ruff'"
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
    lint_cmd = [str(python_executable), "-m", "ruff", "check"] + lint_args

    # If no arguments were passed, use default target directories.
    # This prevents ruff from running on the entire project root by default.
    if not lint_args:
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

    console.print("[bold green]\nRunning[/bold green] linter on codebase\n")
    time.sleep(0.5)

    # Run the linter. Output is streamed directly to the console.
    subprocess.run(lint_cmd)

    console.print("\n[bold green]Linting[/bold green] process completed.")
