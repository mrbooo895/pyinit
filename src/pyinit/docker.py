# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'docker' command for the pyinit command-line tool.

This module is responsible for generating a best-practice `Dockerfile` and
a `.dockerignore` file for a Python project. It automates the process of
creating a containerization setup that is efficient, secure, and ready for
production environments.
"""

import re
import sys

from rich.console import Console

from .utils import check_project_root, find_project_root, get_project_name
from .wrappers import error_handling

# Conditional import of TOML library for Python version compatibility.
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def get_python_version_from_specifier(specifier: str) -> str:
    """
    Parses a Python version specifier string to extract a major.minor version.

    It specifically looks for '>=' specifiers (e.g., '>=3.10') and falls back
    to a default version if the pattern is not found.

    :param str specifier: The `requires-python` string from `pyproject.toml`.
    :return: A 'major.minor' version string (e.g., '3.10').
    :rtype: str
    """
    match = re.search(r">=\s*(\d+\.\d+)", specifier)
    if match:
        return match.group(1)
    return "3.11"  # A safe, modern default


@error_handling
def gen_docker_files():
    """
    Generates `Dockerfile` and `.dockerignore` files for the project.

    This function serves as the entry point for the 'pyinit dockerize' command.
    It reads project metadata to determine the Python version, generates file
    contents based on best practices (multi-stage builds, non-root user),
    and writes them to the project root after confirming with the user if they
    already exist.

    :raises SystemExit: If not run within a valid project or if file writing fails.
    """
    console = Console()
    project_root = find_project_root()

    # --- Pre-flight Checks ---
    check_project_root(project_root)

    dockerfile_path = project_root / "Dockerfile"
    dockerignore_path = project_root / ".dockerignore"

    # Safety check to prevent overwriting existing user configurations without consent.
    if dockerfile_path.exists() or dockerignore_path.exists():
        console.print(
            "[bold yellow][WARNING][/bold yellow] Dockerfile or .dockerignore already exists."
        )
        confirm = console.input("Do you want to overwrite them? (y/N): ")
        if confirm.lower() != "y":
            console.print(
                "[bold yellow][INFO][/bold yellow] Operation cancelled by user"
            )
            sys.exit(0)

    console.print(
        "[bold green]    Generating[/bold green] Docker configuration files..."
    )

    # --- Gather Project Metadata ---
    # Fetch project name and Python version to customize the generated files.
    project_name = get_project_name(project_root) or "app"
    pyproject_path = project_root / "pyproject.toml"
    python_version = "3.11"  # Default version

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        python_specifier = data.get("project", {}).get("requires-python", ">=3.11")
        python_version = get_python_version_from_specifier(python_specifier)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        console.print(
            "[dim yellow][WARNING][/dim yellow] Could not read 'pyproject.toml' for Python version. Defaulting to 3.11."
        )

    # --- Define File Contents ---
    # A multi-stage Dockerfile for smaller, more secure final images.
    dockerfile_content = f"""
# ---- Builder Stage ----
# Use an official Python runtime as a parent image
FROM python:{python_version}-slim as builder

# Set the working directory
WORKDIR /app

# Install build dependencies
RUN pip install --upgrade pip
RUN pip install build

# Copy project definition and build the wheel
COPY pyproject.toml .
RUN python -m build

# ---- Runner Stage ----
# Use a slim, official Python runtime as the final image
FROM python:{python_version}-slim

# Set the working directory
WORKDIR /app

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Copy the built wheel from the builder stage
COPY --from=builder /app/dist/*.whl .

# Install the wheel
RUN pip install *.whl

# Copy the application source code (optional, useful if app reads data files)
COPY src/{project_name} ./src/{project_name}

# Command to run the application
# Note: You might need to change this command based on your project's entry point
CMD ["python", "-m", "{project_name}.main"]
"""

    # A comprehensive .dockerignore to keep the build context small and fast.
    dockerignore_content = """
# Git
.git
.gitignore

# Docker
Dockerfile
.dockerignore

# Python virtual environment
venv/
.venv/

# Python cache
__pycache__/
*.pyc

# Build artifacts
dist/
build/
*.egg-info/

# IDE and OS files
.idea/
.vscode/
.DS_Store
"""

    # --- Write Files to Disk ---
    try:
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content.strip())
        console.print(
            f"[bold green]     Created[/bold green] 'Dockerfile' using Python {python_version}"
        )

        with open(dockerignore_path, "w") as f:
            f.write(dockerignore_content.strip())
        console.print("[bold green]     Created[/bold green] '.dockerignore'")

        console.print("\n[bold green]Successfully[/bold green] generated Docker files.")
        console.print(
            f"[cyan]->[/] You can now build your image with: 'docker build -t {project_name}'"
        )
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] Failed to write Docker files: {e}")
        sys.exit(1)
