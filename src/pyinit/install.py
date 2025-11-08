# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'install' command for the pyinit command-line tool.

This module contains the logic for intelligently installing one or more Python
packages. It checks if packages are already installed before attempting to
install them. After a successful installation, it automatically updates the
`requirements.txt` file to lock the new dependency state.
"""

import subprocess
import sys
from pathlib import Path

from rich.console import Console

from .utils import (
    check_platform,
    check_project_root,
    check_venv_exists,
    find_project_root,
)
from .wrappers import error_handling


def update_requirements(project_root: Path, pip_executable: Path, console: Console):
    """
    Updates the requirements.txt file by running 'pip freeze'.

    This function is called after a successful package installation or
    uninstallation to ensure the lock file is synchronized with the
    virtual environment's state.

    :param Path project_root: The root directory of the project.
    :param Path pip_executable: The path to the venv's pip executable.
    :param Console console: The rich Console instance for printing messages.
    """
    requirements_file = project_root / "requirements.txt"
    try:
        # Run 'pip freeze' to get an exact list of installed packages.
        result = subprocess.run(
            [str(pip_executable), "freeze"], check=True, capture_output=True, text=True
        )
        # Overwrite the requirements file with the new state.
        with open(requirements_file, "w") as f:
            f.write(result.stdout)
    except Exception as e:
        # Warn the user if the lock file update fails, but don't exit,
        # as the primary installation task was successful.
        console.print(
            f"\n[bold yellow][WARNING][/bold yellow] Failed to update '{requirements_file.name}'\n[green]->[/] {e}"
        )


@error_handling
def install_modules(modules_to_install: list):
    """
    Installs one or more Python modules if not already present, and updates requirements.txt.

    This function serves as the primary entry point for the 'pyinit install' command.
    It checks which requested packages are already installed, attempts to install
    only the missing ones, and then regenerates the `requirements.txt` file.

    :param list modules_to_install: A list of package names to install.
    :raises SystemExit: If not run within a valid project, if the venv is not
                        found, or if the installation fails.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)
    venv_dir = project_root / "venv"
    check_venv_exists(venv_dir)

    # --- Determine Platform-specific Executables ---
    pip_executable, _ = check_platform(venv_dir)

    # --- Verify which packages are already installed ---
    try:
        freeze_result = subprocess.run(
            [str(pip_executable), "freeze"], check=True, capture_output=True, text=True
        )
        installed_packages = {
            line.split("==")[0].lower().replace("-", "_")
            for line in freeze_result.stdout.strip().split("\n")
        }
    except Exception:
        console.print(
            "[bold red][ERROR][/bold red] Could not list installed packages from venv."
        )
        sys.exit(1)

    # Filter the user's list to only include packages that are not already installed.
    packages_to_actually_install = []
    for module in modules_to_install:
        # We only check the base name, ignoring version specifiers for this check.
        base_module_name = (
            module.split("==")[0]
            .split(">")[0]
            .split("<")[0]
            .split("~")[0]
            .split("!=")[0]
        )
        normalized_module = base_module_name.lower().replace("-", "_")
        if normalized_module not in installed_packages:
            packages_to_actually_install.append(module)
        else:
            console.print(
                f"[bold yellow][INFO][/] Requirement already satisfied: '{module}'"
            )

    if not packages_to_actually_install:
        console.print(
            "[bold green]\n->[/] All specified packages are already installed, nothing to do."
        )
        sys.exit(0)

    # --- Installation Process ---
    modules_str = ", ".join(f"'{m}'" for m in packages_to_actually_install)
    console.print(f"[bold green]    Installing[/bold green] module(s) {modules_str}")

    try:
        install_cmd = [str(pip_executable), "install"] + packages_to_actually_install
        subprocess.run(
            install_cmd,
            check=True,
            capture_output=True,
        )
        console.print(
            f"[bold green]Successfully[/bold green] Installed {len(packages_to_actually_install)} new package(s)."
        )

        # --- Update Lock File ---
        update_requirements(project_root, pip_executable, console)

    except subprocess.CalledProcessError as e:
        console.print("\n[bold red][ERROR][/bold red] Failed to install packages.")
        if e.stderr:
            console.print(f"[dim red]{e.stderr.decode().strip()}[/dim red]")
        sys.exit(1)
    except Exception as e:
        console.print(
            f"\n[bold red][ERROR][/bold red] An unexpected error occurred: {e}"
        )
        sys.exit(1)
