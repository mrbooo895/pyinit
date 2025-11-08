# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'build' command for the pyinit command-line tool.

This module is responsible for orchestrating the standard Python packaging
process. It ensures the necessary build dependencies are installed and then
invokes the build backend to generate distributable artifacts like wheels
and source distributions (sdist).
"""

import subprocess
import sys

from rich.console import Console

from .utils import (
    check_platform,
    check_project_root,
    find_project_root,
    get_project_name,
)
from .wrappers import error_handling


@error_handling
def build_project():
    """
    Builds the current project into distributable packages.

    This function serves as the main entry point for the 'pyinit build' command.
    It performs the following sequence of operations:
    1. Verifies that it's being run within a valid project.
    2. Installs the standard build tools (`build`, `wheel`) into the project's
       virtual environment to ensure a consistent build environment.
    3. Executes the build process using `python -m build`, which creates the
       packages in the `dist/` directory.

    :raises SystemExit: If the command is not run within a valid project,
                        or if any of the build steps fail.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    # Ensure the command is executed from within a valid project directory.
    check_project_root(project_root)

    venv_dir = project_root / "venv"

    # Attempt to get the project name for better user feedback.
    # If it fails, it will proceed but with less specific messaging.
    project_name = get_project_name(project_root)
    if not project_name:
        console.print(
            "[dim yellow]\n[WARNING][/dim yellow] Could not determine project name from 'pyproject.toml'\n"
        )

    # --- Determine Platform-specific Executables ---
    # The paths to executables within the venv differ based on the OS.
    pip_executable, python_executable = check_platform(venv_dir)
    try:
        # --- Step 1: Install Build Dependencies ---
        # Ensure that the PEP 517 build frontend and backend tools are installed.
        console.print(
            "[bold green]    Fetching[/bold green] Required Build Modules: 'build', 'wheel'"
        )
        subprocess.run(
            [str(pip_executable), "install", "build", "wheel"],
            check=True,
            capture_output=True,
        )

        # --- Step 2: Execute the Build ---
        # Run the standard build process. This reads `pyproject.toml` and
        # creates the sdist and wheel in the `dist/` directory.
        console.print(
            f"[bold green]     Building[/bold green] package '{project_name}'"
        )
        subprocess.run(
            [str(python_executable), "-m", "build"],
            cwd=project_root,
            check=True,
            capture_output=True,
        )

        console.print(
            f"[bold green]\nSuccessfully[/bold green] built package '{project_name}'"
        )
        console.print("[bold green]->[/] Check 'dist/' for results")

    except subprocess.CalledProcessError as e:
        # This catches errors specifically from the subprocess calls,
        # such as a build failure.
        console.print(f"[bold red][ERROR][/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        # A general catch-all for other potential issues (e.g., file permissions).
        console.print(f"[bold red][ERROR][/bold red] {e}")
        sys.exit(1)
