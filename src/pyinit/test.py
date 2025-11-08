# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'test' command for the pyinit command-line tool.

This module provides a convenient wrapper for running tests using the 'pytest'
framework. It handles the automatic installation of pytest if it is not found
and allows for passing additional arguments directly to the pytest runner.
"""

import subprocess
import sys

from rich.console import Console

from .utils import (
    check_platform,
    check_project_root,
    check_venv_exists,
    ensure_tool_installed, 
    find_project_root,
)
from .wrappers import error_handling


@error_handling
def run_tests(pytest_args: list = None):
    """
    Runs the project's tests using pytest.

    This function serves as the main entry point for the 'pyinit test' command.
    It performs the following steps:
    1. Verifies the project context and virtual environment.
    2. Checks if a 'tests/' directory exists (unless specific test files are
       passed as arguments).
    3. Ensures pytest is installed in the virtual environment, installing it
       if necessary.
    4. Executes pytest, passing along any user-provided arguments.

    :param list, optional pytest_args: A list of arguments to be passed directly
                                       to the pytest command. Defaults to None.
    :raises SystemExit: If not run within a valid project, if the virtual
                        environment is not found, or if the installation of
                        pytest fails.
    """
    console = Console()
    project_root = find_project_root()
    if not pytest_args:
        pytest_args = []

    # --- Pre-flight Checks ---
    check_project_root(project_root)
    venv_dir = project_root / "venv"
    check_venv_exists(venv_dir)

    # Check for the 'tests' directory only if the user hasn't specified
    # explicit paths to run.
    tests_dir = project_root / "tests"
    if not tests_dir.exists() and not any(
        arg for arg in pytest_args if not arg.startswith("-")
    ):
        console.print(
            "[bold yellow][INFO][/bold yellow] No 'tests' directory found. Nothing to test."
        )
        sys.exit(0)

    # --- Determine Platform-specific Executables ---
    pip_executable, python_executable = check_platform(venv_dir)

    # --- Ensure Pytest is Installed ---
    # The utility function now handles the check and installation logic.
    ensure_tool_installed(
        pip_executable=pip_executable,
        python_executable=python_executable,
        tool_name="pytest",
        import_name="pytest",
        console=console,
    )

    # --- Run Tests ---
    console.print("[bold green]Running[/bold green] tests...")

    # Construct the command to run pytest as a module.
    run_tests_cmd = [str(python_executable), "-m", "pytest"] + pytest_args

    try:
        # Execute pytest. CWD is set to project root for consistent path discovery.
        # Output is streamed directly to the console.
        subprocess.run(run_tests_cmd, cwd=project_root)
        console.print("\n[bold green]Testing[/bold green] process completed.")
    except Exception as e:
        console.print(
            f"[bold red][ERROR][/bold red] An unexpected error occurred while running tests: {e}"
        )
        sys.exit(1)