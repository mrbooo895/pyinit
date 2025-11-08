# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'run' command for the pyinit command-line tool.

This module is responsible for executing the main entry point of a project.
It abstracts away the need for the user to manually activate the virtual
environment and find the path to the main script. It also supports passing
command-line arguments directly to the user's script.
"""

import subprocess
import sys
import time

from rich.console import Console

from .utils import find_project_root, get_project_name
from .wrappers import error_handling

console = Console()


@error_handling
def run_project(app_args: list = None):
    """
    Executes the project's main script within its virtual environment.

    This function serves as the entry point for the 'pyinit run' command.
    It locates the project, its virtual environment, and its main script
    (assumed to be `src/<package_name>/main.py`), and then runs it as a
    subprocess, passing along any extra arguments.

    :param list, optional app_args: A list of command-line arguments to pass
                                    to the user's script. Defaults to None.
    :raises SystemExit: If not run within a valid project or if critical files
                        (like the main script or venv) are missing.
    """
    project_root = find_project_root()
    if not app_args:
        app_args = []

    # --- Pre-flight Checks ---
    if not project_root:
        console.print(
            "[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'."
        )
        sys.exit(1)

    # Determine project name and construct paths to key files/directories.
    project_name = get_project_name(project_root) or project_root.name
    main_file = project_root / "src" / project_name / "main.py"
    venv_dir = project_root / "venv"

    # Verify that the expected main script exists.
    if not main_file.exists():
        console.print(
            f"[bold red][ERROR][/bold red] Main file '{main_file}' was not found."
        )
        sys.exit(1)

    # Verify that the virtual environment exists.
    if not venv_dir.exists():
        console.print(
            f"[bold red][ERROR][/bold red] Virtual Environment '{venv_dir.name}' not found."
        )
        sys.exit(1)

    # --- Determine Platform-specific Python Executable ---
    if sys.platform == "win32":
        python_executable = venv_dir / "Scripts" / "python.exe"
    else:
        python_executable = venv_dir / "bin" / "python"

    console.print(f"[bold green]    Running[/bold green] package '{project_name}'")
    time.sleep(0.25)

    try:
        # Construct the full command, including the Python interpreter,
        # the script path, and any passthrough arguments.
        run_cmd = [str(python_executable), str(main_file)] + app_args
        # Execute the command. Output is streamed directly to the console.
        subprocess.run(run_cmd, check=True)
    except FileNotFoundError:
        # This error typically occurs if the venv is corrupted and the
        # Python executable itself is missing.
        console.print(
            f"\n[bold red][ERROR][/bold red] Python Executable '{python_executable}' Not Found\n-> The venv might be corrupted."
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        # This error occurs if the user's script exits with a non-zero status code.
        # The error is printed to inform the user about the script's failure.
        console.print(f"\n[bold red][ERROR][/bold red] {e}")
