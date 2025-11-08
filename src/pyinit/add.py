# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'add' command for the pyinit command-line tool.

This module contains the logic for installing a Python package into the active
project's virtual environment. It handles locating the project, verifying the
environment, and executing the installation via pip.
"""

import subprocess

from rich.console import Console

from .utils import (
    check_platform,
    check_project_root,
    check_venv_exists,
    find_project_root,
)
from .wrappers import error_handling


@error_handling
def add_module(module_to_install):
    """
    Installs a specified Python module into the project's virtual environment.

    This function serves as the primary entry point for the 'pyinit add' command.
    It performs several pre-flight checks to ensure a valid project context
    before attempting to install the package using the virtual environment's
    pip executable.

    :param str module_to_install: The name of the Python package to install,
                                  as it would be passed to 'pip install'.
    :raises SystemExit: If the command is not run within a valid project or
                        if the virtual environment is not found.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    # Ensure the command is being run from within a valid project directory.
    check_project_root(project_root)

    module_name = module_to_install
    venv_dir = project_root / "venv"

    # Verify that the virtual environment directory exists.
    check_venv_exists(venv_dir)
    # --- Determine Platform-specific Executables ---
    # The path to pip differs between Windows and Unix-like systems.
    pip_executable, _ = check_platform(venv_dir)

    # --- Installation Process ---
    # Provide visual feedback to the user that the installation is starting.
    console.print(f"[bold green]    Installing[/bold green] module '{module_name}'")

    try:
        # Execute 'pip install' as a subprocess within the virtual environment.
        # 'capture_output=True' prevents pip's output from flooding the console.
        subprocess.run(
            [str(pip_executable), "install", module_name],
            check=True,
            capture_output=True,
        )
        console.print(
            f"[bold green]Successfully[/bold green] Installed '{module_name}'"
        )
    except Exception as e:
        # A generic exception catch-all for any failure during the subprocess run.
        console.print(
            f"\n[bold red][ERROR][/bold red] Failed To Install Module: {module_name}\n-> {e}"
        )
