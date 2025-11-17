# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'release' command for the pyinit command-line tool.

This module is responsible for programmatically incrementing the project's
version number according to Semantic Versioning (SemVer) rules. It reads the
current version, increments the specified part (major, minor, or patch), and
writes the new version back to both `pyproject.toml` and the package's
`__init__.py` file.
"""

import re
import tomllib
from pathlib import Path

import tomli_w
from rich.console import Console

from .utils import check_project_root, find_project_root, get_project_name
from .wrappers import error_handling


def update_init_version(
    project_root: Path, project_name: str, new_version: str
) -> bool:
    """
    Updates the `__version__` variable in the package's `__init__.py` file.

    It uses a regular expression to find and replace the version string,
    which is more robust than simple string replacement.

    :param Path project_root: The root directory of the project.
    :param str project_name: The name of the package.
    :param str new_version: The new version string to write.
    :return: True if the update was successful, False otherwise.
    :rtype: bool
    """
    if not project_name:
        return False

    init_file = project_root / "src" / project_name / "__init__.py"
    if not init_file.is_file():
        return False

    try:
        content = init_file.read_text(encoding="utf-8")
        # Regex to robustly find and replace: __version__ = "..." or __version__ = '...'
        new_content, num_replacements = re.subn(
            r"(__version__\s*=\s*['\"])([^'\"]+)(['\"])",
            rf"\g<1>{new_version}\g<3>",
            content,
            count=1,
        )
        if num_replacements > 0:
            init_file.write_text(new_content, encoding="utf-8")
            return True
        return False  # Return False if no version string was found to replace
    except (IOError, re.error):
        return False


@error_handling
def increase_version(part: str):
    """
    Increments the project version in `pyproject.toml` and `__init__.py`.

    This function serves as the entry point for the 'pyinit release' command.
    It reads the TOML file, parses the current version, calculates the new
    version based on the 'part' to increment, and then overwrites the
    configuration and source files with the updated data.

    :param str part: The part of the version to increment. Must be one of
                     'major', 'minor', or 'patch'.
    :raises SystemExit: If not run within a valid project, if `pyproject.toml`
                        is unreadable, or if the version string is malformed.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)

    pyproject_path = project_root / "pyproject.toml"

    # --- Read and Parse pyproject.toml ---

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    console.print("[bold green]    Setting[/bold green] project version to new release")

    # --- Version Calculation ---

    old_version = data["project"]["version"]
    major, minor, patch = map(int, old_version.split("."))
    # Increment the version based on the specified part, following SemVer rules.
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

    # --- Update pyproject.toml ---
    data["project"]["version"] = new_version
    with open(pyproject_path, "wb") as f:
        tomli_w.dump(data, f)

    # --- Update __init__.py ---
    project_name = get_project_name(project_root)
    init_updated = update_init_version(project_root, project_name, new_version)

    # --- Final User Feedback ---
    console.print(
        f"[bold green]     Updating[/bold green] version from '{old_version}' to '{new_version}'"
    )

    if not init_updated:
        pass

    console.print(
        "\n[bold green]Successfully[/bold green] Released New project version."
    )
