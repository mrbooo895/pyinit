# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'update' command for the pyinit command-line tool.

This module provides functionality to intelligently check for and apply updates
to a project's dependencies. It first checks which packages are actually
outdated before performing any action, making it more efficient and user-friendly.
"""

import subprocess
import sys

from rich.console import Console

# Import the shared utility function from the 'install' module.
from .install import update_requirements
from .utils import (
    check_platform,
    check_project_root,
    check_venv_exists,
    find_project_root,
)
from .wrappers import error_handling


@error_handling
def update_modules(upgrade: bool = False):
    """
    Checks for or applies updates to project dependencies intelligently.

    This function is the entry point for the 'pyinit update' command. It first
    runs `pip list --outdated` to identify which packages have updates.
    - If `upgrade` is False, it displays this list.
    - If `upgrade` is True, it proceeds to upgrade only those outdated packages.
    It exits gracefully if all packages are already up-to-date.

    :param bool upgrade: If True, upgrades outdated packages. If False, only
                         checks for them. Defaults to False.
    :raises SystemExit: If not run in a valid project or if a subprocess fails.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)
    venv_dir = project_root / "venv"
    check_venv_exists(venv_dir)

    # --- Determine Platform-specific Executables ---
    pip_executable, _ = check_platform(venv_dir)

    # --- Step 1: Always check for outdated packages first ---
    console.print("[bold green]    Checking[/bold green] for new module(s) versions")
    check_cmd = [str(pip_executable), "list", "--outdated"]
    try:
        outdated_result = subprocess.run(check_cmd, capture_output=True, text=True)
        # Pip's `list --outdated` returns a non-zero exit code if it finds nothing,
        # so we check the output content instead of the return code.
        # The output header is 2 lines long.
        outdated_packages_output = outdated_result.stdout.strip()
        has_updates = len(outdated_packages_output.splitlines()) > 2
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] Failed to check for updates: {e}")
        sys.exit(1)

    # --- Step 2: Decide action based on check results ---
    if not has_updates:
        console.print(
            "[bold green]\n->[/bold green] All modules are up to date, nothing to do."
        )
        sys.exit(0)

    if upgrade:
        # --- Upgrade Mode ---
        # Parse the output to get the names of outdated packages.
        packages_to_upgrade = [
            line.split()[0] for line in outdated_packages_output.splitlines()[2:]
        ]

        console.print(
            f"[bold green]     Found[/bold green] {len(packages_to_upgrade)} module(s) to upgrade."
        )

        try:
            upgrade_cmd = [
                str(pip_executable),
                "install",
                "--upgrade",
            ] + packages_to_upgrade
            subprocess.run(upgrade_cmd, check=True)
            console.print(
                "\n[bold green]Successfully[/bold green] upgraded all modules."
            )
            # Update the lock file after a successful upgrade.
            update_requirements(project_root, pip_executable, console)

        except subprocess.CalledProcessError as e:
            console.print("[bold red][ERROR][/bold red] Failed to upgrade modules.")
            if e.stderr:
                console.print(f"[red]{e.stderr.decode()}[/red]")
            sys.exit(1)

    else:
        # --- Check-Only Mode ---
        # Simply print the list of outdated packages that we already fetched.
        console.print(outdated_packages_output)
        console.print(
            "\n[bold green]Run:[/bold green]\n     'pyinit update --upgrade' to apply these updates."
        )
