# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Provides shared utility functions used across the pyinit application.

This module contains common helper functions for tasks such as locating the
project root, setting up logging, and parsing `pyproject.toml` for metadata.
"""

import re
import sys
from pathlib import Path

from rich.console import Console

# Conditional import of TOML library for Python version compatibility.
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

console = Console()


def find_project_root() -> Path | None:
    """
    Finds the project root by searching upwards for a `pyproject.toml` file.

    :return: A Path object to the project root, or None if not found.
    :rtype: Path or None
    """
    current_dir = Path.cwd().resolve()
    while current_dir != current_dir.parent:
        if (current_dir / "pyproject.toml").is_file():
            return current_dir
        current_dir = current_dir.parent
    # Final check for the filesystem root directory itself.
    if (current_dir / "pyproject.toml").is_file():
        return current_dir
    return None


def get_project_name(project_root: Path) -> str | None:
    """
    Parses `pyproject.toml` to extract the project's name.

    :param Path project_root: The root directory of the project.
    :return: The project name, or None if not found or on error.
    :rtype: str or None
    """

    pyproject_path = project_root / "pyproject.toml"
    try:
        with open(pyproject_path, "rb") as file:
            data = tomllib.load(file)

        return data.get("project", {}).get("name")

    except (tomllib.TOMLDecodeError, FileNotFoundError):
        return None


def get_project_dependencies(project_root: Path) -> list[str]:
    """
    Parses `pyproject.toml` to extract all declared dependencies.

    This includes both standard dependencies and all optional dependency groups.

    :param Path project_root: The root directory of the project.
    :return: A list of dependency names, stripped of version specifiers.
    :rtype: list[str]
    """
    pyproject_path = project_root / "pyproject.toml"
    dependencies = []
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        # Get main dependencies
        if "project" in data and "dependencies" in data["project"]:
            dependencies.extend(data["project"]["dependencies"])

        # Get all optional dependencies (e.g., [dev, test])
        if "project" in data and "optional-dependencies" in data["project"]:
            for group in data["project"]["optional-dependencies"].values():
                dependencies.extend(group)

        # Clean names, removing version specifiers (e.g., "requests>=2.0" -> "requests")
        cleaned_deps = [
            re.split(r"[<>=!~]", dep)[0].strip() for dep in dependencies if dep.strip()
        ]
        # Return a unique list of dependencies.
        return list(set(cleaned_deps))

    except (tomllib.TOMLDecodeError, FileNotFoundError):
        return []


def check_project_root(proj_root):
    if not proj_root:
        console.print(
            "[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'."
        )
        sys.exit(1)


def check_venv_exists(venv_dir):
    if not venv_dir.exists():
        console.print(
            f"[bold red][ERROR][/bold red] Virtual Environment '{venv_dir.name}' not found"
        )
        sys.exit(1)


def check_platform(venv_directory):
    if sys.platform == "win32":
        python_executable = venv_directory / "Scripts" / "python.exe"
        pip_executable = venv_directory / "Scripts" / "pip.exe"
    else:
        python_executable = venv_directory / "bin" / "python"
        pip_executable = venv_directory / "bin" / "pip"
    return pip_executable, python_executable
