# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'release' command for the pyinit command-line tool.

This module is responsible for programmatically incrementing the project's
version number according to Semantic Versioning (SemVer) rules. It reads the
current version from `pyproject.toml`, increments the specified part (major,
minor, or patch), and writes the new version back to the file.
"""

import sys

import tomli_w
from rich.console import Console

from .utils import check_project_root, find_project_root
from .wrappers import error_handling

# Conditional import of TOML library for Python version compatibility.
# `tomllib` is standard in Python 3.11+, `tomli` is used for older versions.
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@error_handling
def increase_version(part: str):
    """
    Increments the project version in `pyproject.toml`.

    This function serves as the entry point for the 'pyinit release' command.
    It reads the TOML file, parses the current version, calculates the new
    version based on the 'part' to increment, and then overwrites the file
    with the updated data.

    :param str part: The part of the version to increment. Must be one of
                     'major', 'minor', or 'patch'.
    :raises SystemExit: If not run within a valid project, if the `pyproject.toml`
                        is unreadable, or if the version string is malformed.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)

    pyproject_path = project_root / "pyproject.toml"

    # --- Read and Parse pyproject.toml ---
    try:
        # File is opened in binary mode ('rb') as required by tomllib.
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, FileNotFoundError):
        console.print(
            f"[bold red][ERROR][/bold red] Could not read or parse '{pyproject_path.name}'."
        )
        sys.exit(1)

    console.print("[bold green]    Setting[/bold green] project version to new release")

    # --- Version Calculation ---
    try:
        # Extract and parse the current version string.
        old_version = data["project"]["version"]
        major, minor, patch = map(int, old_version.split("."))
    except (KeyError, ValueError):
        # Handle cases where the version key is missing or not in 'X.Y.Z' format.
        console.print(
            f"[bold red][ERROR][/bold red] Invalid or missing version string in '{pyproject_path.name}'. Expected format: 'X.Y.Z'"
        )
        sys.exit(1)
    else:
        # This block only executes if the `try` block succeeds.
        # Increment the version based on the specified part, following SemVer rules
        # (e.g., bumping 'minor' resets 'patch' to 0).
        if part == "major":
            major += 1
            minor = 0
            patch = 0
        elif part == "minor":
            minor += 1
            patch = 0
        elif part == "patch":
            patch += 1

        new_version = f"{major}.{minor}.{patch}"
        data["project"]["version"] = new_version

        # --- Write Updated pyproject.toml ---
        try:
            # File is opened in binary write mode ('wb') for tomli_w.
            with open(pyproject_path, "wb") as f:
                tomli_w.dump(data, f)
        except Exception as e:
            console.print(
                f"[bold red][ERROR][/bold red] Failed to write updated version to '{pyproject_path.name}': {e}"
            )
            sys.exit(1)

        console.print(
            f"[bold green]     Updating[/bold green] version from [yellow]{old_version}[/yellow] to [cyan]{new_version}[/cyan]"
        )
        console.print(
            "\n[bold green]Successfully[/bold green] Released New project version."
        )
