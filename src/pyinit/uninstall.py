# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'uninstall' command for the pyinit command-line tool.

This module contains the logic for removing one or more Python packages from
the active project's virtual environment. It verifies which packages are
actually installed before prompting for removal, and after a successful
uninstallation, it automatically updates the `requirements.txt` file.
"""

import subprocess
import sys
from pathlib import Path

from rich.console import Console

# Import the shared utility function from the 'install' module.
from .install import update_requirements
from .utils import check_platform, check_project_root, check_venv_exists, find_project_root
from .wrappers import error_handling


@error_handling
def uninstall_modules(modules_to_uninstall: list):
    """
    Uninstalls one or more Python modules and updates requirements.txt.

    This function serves as the primary entry point for the 'pyinit uninstall'
    command. It first checks which of the requested packages are actually
    installed, prompts the user for confirmation on that filtered list,
    uninstalls them, and then regenerates the `requirements.txt` file.

    :param list modules_to_uninstall: A list of package names to uninstall.
    :raises SystemExit: If not run within a valid project, if the venv is not
                        found, if the user cancels, or if uninstallation fails.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)
    venv_dir = project_root / "venv"
    check_venv_exists(venv_dir)

    # --- Determine Platform-specific Executables ---
    pip_executable, _ = check_platform(venv_dir)

    # --- Verify which packages are actually installed ---
    try:
        freeze_result = subprocess.run(
            [str(pip_executable), "freeze"],
            check=True,
            capture_output=True,
            text=True
        )
        # Create a set of normalized installed package names for fast lookups.
        installed_packages = {
            line.split("==")[0].lower().replace("-", "_")
            for line in freeze_result.stdout.strip().split("\n")
        }
    except Exception:
        console.print("[bold red][ERROR][/bold red] Could not list installed packages from venv.")
        sys.exit(1)

    # Filter the user's list to only include packages that are actually installed.
    packages_to_actually_uninstall = []
    for module in modules_to_uninstall:
        normalized_module = module.lower().replace("-", "_")
        if normalized_module in installed_packages:
            packages_to_actually_uninstall.append(module)
        else:
            console.print(f"[bold yellow][INFO][/] Package '{module}' is not installed")
    
    if not packages_to_actually_uninstall:
        console.print("[green]\n->[/] Nothing to uninstall.")
        sys.exit(0)

    # --- Confirmation Phase ---
    modules_str = ", ".join(f"'{m}'" for m in packages_to_actually_uninstall)
    console.print(f"[bold green]->[/] The following packages will be uninstalled: {modules_str}")
    
    try:
        confirm = console.input("Are you sure you want to proceed? (y/N): ")
        if confirm.lower() != "y":
            console.print("[bold yellow][INFO][/bold yellow] Operation cancelled by user.")
            sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold yellow][INFO][/bold yellow] Operation cancelled by user.")
        sys.exit(0)

    # --- Uninstallation Process ---
    console.print(f"[bold green]    Uninstalling[/bold green] {modules_str}")

    try:
        uninstall_cmd = [str(pip_executable), "uninstall", "-y"] + packages_to_actually_uninstall
        subprocess.run(
            uninstall_cmd,
            check=True,
            capture_output=True,
        )
        console.print(
            f"[bold green]Successfully[/bold green] Uninstalled {len(packages_to_actually_uninstall)} package(s)."
        )

        # --- Update Lock File ---
        update_requirements(project_root, pip_executable, console)

    except subprocess.CalledProcessError as e:
        console.print(f"\n[bold red][ERROR][/bold red] Failed to uninstall packages.")
        if e.stderr:
            console.print(f"[dim red]{e.stderr.decode().strip()}[/dim red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red][ERROR][/bold red] An unexpected error occurred: {e}")
        sys.exit(1)