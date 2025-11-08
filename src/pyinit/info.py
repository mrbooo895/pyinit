# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'info' command for the pyinit command-line tool.

This module gathers and displays a comprehensive summary of the current project.
It aggregates metadata from `pyproject.toml`, statistics from the filesystem
and virtual environment, and status information from the Git repository to
provide a complete project dashboard.
"""

import datetime
import subprocess
import sys
from pathlib import Path

from rich.console import Console

from .utils import check_platform, check_project_root, find_project_root
from .wrappers import error_handling

# Conditional import of TOML library for Python version compatibility.
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def run_command(command: list[str], cwd: Path) -> str | None:
    """
    Executes a shell command and returns its stripped stdout.

    A utility function to safely run subprocesses and handle potential errors.

    :param list[str] command: The command and its arguments as a list of strings.
    :param Path cwd: The working directory in which to run the command.
    :return: The stripped standard output of the command, or None if it fails.
    :rtype: str or None
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_venv_info(project_root: Path) -> tuple[str, str]:
    """
    Retrieves information from the project's virtual environment.

    :param Path project_root: The root directory of the project.
    :return: A tuple containing the Python version string and the total
             number of installed packages.
    :rtype: tuple[str, str]
    """
    venv_dir = project_root / "venv"
    if not venv_dir.exists():
        return "[dim]N/A[/dim]", "0"

    pip_executable, python_executable = check_platform(venv_dir)

    if not python_executable.exists():
        return "[dim]N/A[/dim]", "0"

    version = run_command([str(python_executable), "--version"], project_root)
    packages_output = run_command([str(pip_executable), "list"], project_root)
    packages_count = (
        len(packages_output.splitlines()) - 2
        if packages_output and len(packages_output.splitlines()) > 2
        else 0
    )

    return version or "[dim]N/A[/dim]", str(packages_count)


def get_project_stats(project_root: Path) -> tuple[int, int, str]:
    """
    Calculates filesystem statistics for the project's source code.

    :param Path project_root: The root directory of the project.
    :return: A tuple containing the total number of Python files, total lines
             of code, and the timestamp of the last modified file in `src/`.
    :rtype: tuple[int, int, str]
    """
    total_files = 0
    total_lines = 0
    latest_mod_time = 0.0
    src_dir = project_root / "src"

    if src_dir.is_dir():
        py_files = list(src_dir.rglob("*.py"))
        total_files = len(py_files)
        for path in py_files:
            try:
                mod_time = path.stat().st_mtime
                if mod_time > latest_mod_time:
                    latest_mod_time = mod_time
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    total_lines += len(f.readlines())
            except Exception:
                continue

    last_modified = (
        datetime.datetime.fromtimestamp(latest_mod_time).strftime("%Y-%m-%d %H:%M:%S")
        if latest_mod_time > 0
        else "[dim]N/A[/dim]"
    )
    return total_files, total_lines, last_modified


@error_handling
def project_info():
    """
    Gathers and displays a comprehensive dashboard of project information.

    This function is the entry point for the 'pyinit info' command. It aggregates
    data from `pyproject.toml`, the virtual environment, the filesystem, and Git
    to present a detailed, formatted summary to the user.

    :raises SystemExit: If not run within a valid project or if `pyproject.toml`
                        is unreadable.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)

    pyproject_path = project_root / "pyproject.toml"

    console.print("[bold green]    Generating[/bold green] Information Table")

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        project_data = data.get("project", {})
    except (tomllib.TOMLDecodeError, FileNotFoundError):
        console.print(
            f"[bold red][ERROR][/bold red] Could not read or parse '{pyproject_path.name}'."
        )
        sys.exit(1)

    # --- Data Gathering ---
    # Collect all necessary information from different sources before printing.
    venv_python, venv_packages = get_venv_info(project_root)
    files, lines, last_mod = get_project_stats(project_root)
    creation_time = datetime.datetime.fromtimestamp(
        project_root.stat().st_ctime
    ).strftime("%Y-%m-%d %H:%M:%S")
    branch = run_command(["git", "branch", "--show-current"], project_root)

    # --- Formatted Output ---
    # Display the gathered information in a structured, readable format.
    console.print(f"  Name           : {project_data.get('name', '[dim]N/A[/dim]')}")
    console.print(f"  Version        : {project_data.get('version', '[dim]N/A[/dim]')}")
    console.print(
        f"  Description    : {project_data.get('description', '[dim]N/A[/dim]')}"
    )
    authors = ", ".join([a.get("name", "") for a in project_data.get("authors", [])])
    console.print(f"  Authors        : {authors or '[dim]N/A[/dim]'}")
    license_info = project_data.get("license", {})
    license_text = (
        license_info.get("text")
        if isinstance(license_info, dict)
        else str(license_info)
    )
    console.print(f"  License        : {license_text or '[dim]N/A[/dim]'}")

    console.print(f"  Project Path   : {project_root}")
    console.print(f"  Created On     : [dim white]{creation_time}[/]")
    console.print(f"  Last Modified  : [dim white]{last_mod}[/] (in src)")
    console.print(
        f"  Python Req.    : {project_data.get('requires-python', '[dim]N/A[/dim]')}"
    )
    console.print(f"  Venv Python    : {venv_python}")
    console.print(f"  Venv Packages  : {venv_packages} installed")
    console.print(f"  Files (in src) : {files}")
    console.print(f"  Lines (in src) : {lines:,}")

    if branch is not None:
        latest_commit = run_command(
            ["git", "log", "-1", "--pretty=%h (%cr): %s"], project_root
        )
        status_output = run_command(["git", "status", "--porcelain"], project_root)
        status = (
            "[green]Clean[/]"
            if not status_output
            else "[bold yellow]Dirty[/] (uncommitted changes)"
        )

        console.print(f"  Branch         : [bold yellow]{branch}[/]")
        console.print(f"  Last Commit    : {latest_commit}")
        console.print(f"  Status         : {status}")
    else:
        console.print("  [dim]Not a Git repository.[/dim]")

    console.print()
