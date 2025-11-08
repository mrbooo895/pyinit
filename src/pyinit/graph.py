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
import time

from rich.console import Console

from .utils import find_project_root
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

    # --- Ensure pipdeptree is Installed ---
    console.print("[bold green]    Checking[/bold green] for 'pipdeptree'")
    time.sleep(0.25)

    check_tool_cmd = [str(python_executable), "-c", "import pipdeptree"]
    tool_installed = subprocess.run(check_tool_cmd, capture_output=True).returncode == 0

    if not tool_installed:
        console.print(
            "[bold green]     Installing[/bold green] Required Module 'pipdeptree'"
        )
        install_cmd = [str(pip_executable), "install", "pipdeptree"]
        try:
            subprocess.run(install_cmd, check=True, capture_output=True)
            console.print(
                "[bold green]      Successfully[/bold green] installed 'pipdeptree'"
            )
        except subprocess.CalledProcessError as e:
            console.print("[bold red][ERROR][/bold red] Failed to install pipdeptree.")
            console.print(f"[red]{e.stderr.decode()}[/red]")
            sys.exit(1)
    else:
        console.print("[bold green]     Found[/bold green] Module 'pipdeptree'")
        time.sleep(0.5)

    # --- Generate and Display the Graph ---
    console.print("[bold green]\nGenerating[/bold green] dependency graph...\n")
    time.sleep(1)

    graph_cmd = [str(python_executable), "-m", "pipdeptree"]

    # The output of pipdeptree is streamed directly to the user's console.
    subprocess.run(graph_cmd)

    console.print("\n[bold green]Graph[/bold green] generation completed.")
