# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'update' command for the pyinit command-line tool.

This module provides functionality to check for and apply updates to a
project's dependencies. It offers two modes: a check-only mode that lists
outdated packages, and an upgrade mode that actively updates the declared
dependencies from `pyproject.toml`.
"""

import subprocess
import sys

from rich.console import Console

from .utils import (
    check_platform,
    check_project_root,
    check_venv_exists,
    find_project_root,
    get_project_dependencies,
)
from .wrappers import error_handling


@error_handling
def update_modules(upgrade: bool = False):
    """
    Checks for or applies updates to project dependencies.

    This function serves as the main entry point for the 'pyinit update' command.
    - If `upgrade` is False (default), it runs `pip list --outdated` to show
      available updates without making changes.
    - If `upgrade` is True, it reads the direct dependencies from `pyproject.toml`
      and runs `pip install --upgrade` on them.

    :param bool upgrade: If True, upgrades packages. If False, only checks for
                         outdated packages. Defaults to False.
    :raises SystemExit: If not run within a valid project or if the virtual
                        environment is missing.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)

    venv_dir = project_root / "venv"
    check_venv_exists(venv_dir)

    # --- Determine Platform-specific Executables ---
    pip_executable, _ = check_platform(venv_dir)

    if upgrade:
        # --- Upgrade Mode ---
        # Actively installs the latest versions of declared dependencies.
        console.print("[bold green]    Upgrading[/bold green] project dependencies...")

        # Fetch the list of direct dependencies from the project's config.
        project_deps = get_project_dependencies(project_root)

        if not project_deps:
            console.print(
                "[bold yellow][INFO][/bold yellow] No project dependencies found in 'pyproject.toml' to upgrade."
            )
            sys.exit(0)

        console.print(
            f"[bold green]     Found[/bold green] {len(project_deps)} direct dependencies to check."
        )

        try:
            # Construct and run the 'pip install --upgrade' command.
            upgrade_cmd = [str(pip_executable), "install", "--upgrade"] + project_deps
            subprocess.run(upgrade_cmd, check=True)
            console.print(
                "\n[bold green]Successfully[/bold green] updated project dependencies."
            )
        except subprocess.CalledProcessError as e:
            console.print("[bold red][ERROR][/bold red] Failed to upgrade packages.")
            console.print(f"[red]{e.stderr.decode()}[/red]")
            sys.exit(1)

    else:
        # --- Check-Only Mode ---
        # Lists outdated packages without installing them.
        console.print("[bold green]    Checking[/bold green] for outdated packages...")

        check_cmd = [str(pip_executable), "list", "--outdated"]

        try:
            # Run 'pip list --outdated' and stream its output to the console.
            subprocess.run(check_cmd)
            console.print(
                "\n[bold green]Run:[/bold green]\n     'pyinit update --upgrade' to upgrade project dependencies."
            )
        except Exception as e:
            console.print(
                f"[bold red][ERROR][/bold red] Failed to check for updates: {e}"
            )
            sys.exit(1)
