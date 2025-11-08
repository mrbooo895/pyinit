# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'graph' command for the pyinit command-line tool.

This module provides a convenient way to visualize the project's dependency
tree. It uses the 'pipdeptree' package to generate and display a hierarchical
view of installed packages and their sub-dependencies, which is invaluable
for debugging dependency conflicts.
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
def show_dependency_graph():
    """
    Displays the project's dependency graph using pipdeptree.

    This function serves as the main entry point for the 'pyinit graph' command.
    It handles the automatic installation of 'pipdeptree' if it's not present
    in the virtual environment and then executes it to print the dependency
    tree directly to the console.

    :raises SystemExit: If not run within a valid project, if the virtual
                        environment is not found, or if the installation of
                        pipdeptree fails.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)
    venv_dir = project_root / "venv"
    check_venv_exists(venv_dir)

    # --- Determine Platform-specific Executables ---
    pip_executable, python_executable = check_platform(venv_dir)

    # --- Ensure pipdeptree is Installed ---
    # The logic for checking and installing is now handled by this utility.
    ensure_tool_installed(
        pip_executable=pip_executable,
        python_executable=python_executable,
        tool_name="pipdeptree",
        import_name="pipdeptree",
        console=console,
    )

    # --- Generate and Display the Graph ---
    console.print("[bold green]\nGenerating[/bold green] dependency graph\n")

    graph_cmd = [str(python_executable), "-m", "pipdeptree"]

    # The output of pipdeptree is streamed directly to the user's console.
    subprocess.run(graph_cmd)

    console.print("\n[bold green]Graph[/bold green] generation completed.")