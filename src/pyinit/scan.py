# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Implements the 'scan' command for the pyinit command-line tool.

This module provides a diagnostic tool to scan a project's structure and
configuration for common issues and deviations from best practices. It acts
as a "doctor" for the project, reporting on its health and providing
suggestions for fixes.
"""

import subprocess
import sys
import time

from rich.console import Console

from .utils import find_project_root, get_project_dependencies
from .wrappers import error_handling

# Conditional import of TOML library for Python version compatibility.
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class ProjectScanner:
    """
    A class that encapsulates the logic for scanning a project.

    It is designed to be instantiated with a console and project root, and then
    run a series of predefined check methods. It tracks the results and can
    print a final summary of its findings.
    """

    def __init__(self, console, project_root):
        """
        Initializes the ProjectScanner.

        :param Console console: An instance of rich.console.Console for output.
        :param Path project_root: The root path of the project to be scanned.
        """
        self.console = console
        self.project_root = project_root
        self.checks_passed = 0
        self.total_checks = 0
        self.issues = []

    def run_check(self, title, check_func):
        """
        Executes a single check function and reports its status.

        This runner method provides consistent output formatting for each check,
        displaying a title and a pass/fail status. It updates the internal
        counters and stores issue messages upon failure.

        :param str title: A user-friendly title for the check being performed.
        :param function check_func: The check function to execute. This function
                                    must return a tuple (bool, str) indicating
                                    success and an issue message if applicable.
        """
        self.total_checks += 1
        self.console.print(f"[bold green]     Checking[/bold green] {title}:", end="")
        time.sleep(0.15)
        success, message = check_func()
        if success:
            self.console.print(" [bold green]OK[/bold green]")
            self.checks_passed += 1
        else:
            self.console.print(" [bold red]FAIL[/bold red]")
            self.issues.append(message)

    def check_pyproject_exists(self):
        """Checks for the existence of the `pyproject.toml` file."""
        if (self.project_root / "pyproject.toml").is_file():
            return True, ""
        return (
            False,
            "[bold red]FATAL:[/] 'pyproject.toml' not found. This is not a valid project.",
        )

    def check_pyproject_parsable(self):
        """Checks if `pyproject.toml` is a valid, parsable TOML file."""
        try:
            with open(self.project_root / "pyproject.toml", "rb") as f:
                tomllib.load(f)
            return True, ""
        except tomllib.TOMLDecodeError:
            return (
                False,
                "[bold red]ERROR:[/] 'pyproject.toml' is malformed and cannot be read.",
            )

    def check_src_layout(self):
        """Checks for the presence of the standard `src/` directory."""
        if (self.project_root / "src").is_dir():
            return True, ""
        return False, "[bold yellow]WARNING:[/] Standard 'src' directory is missing."

    def check_venv_exists(self):
        """Checks for the presence of the `venv/` virtual environment directory."""
        if (self.project_root / "venv").is_dir():
            return True, ""
        return (
            False,
            "[bold red]ERROR:[/] 'venv' directory not found. Dependencies are not isolated.\n       -> [cyan]Suggestion:[/] Run 'pyinit venv create'",
        )

    def check_git_initialized(self):
        """Checks if the project directory is a Git repository."""
        if (self.project_root / ".git").is_dir():
            return True, ""
        return (
            False,
            "[bold yellow]WARNING:[/] Project is not a Git repository.\n       -> [yellow]Suggestion:[/] Run 'git init'",
        )

    def check_gitignore_exists(self):
        """Checks for the presence of a `.gitignore` file."""
        if (self.project_root / ".gitignore").is_file():
            return True, ""
        return False, "[bold yellow]WARNING:[/] '.gitignore' file is missing."

    def check_tests_dir_exists(self):
        """Checks for the presence of a `tests/` directory, encouraging testing."""
        if (self.project_root / "tests").is_dir():
            return True, ""
        return (
            False,
            "[bold yellow]WARNING:[/] 'tests' directory not found.",
        )

    def check_dependencies_synced(self):
        """
        Verifies if dependencies in `pyproject.toml` are installed in the venv.

        This is a critical check for environment consistency. It compares the output
        of `pip freeze` with the dependencies declared in the project's
        configuration file.
        """
        venv_dir = self.project_root / "venv"
        if not venv_dir.is_dir():
            return (
                False,
                "[bold red]ERROR:[/] Cannot check dependencies because 'venv' is missing.",
            )

        if sys.platform == "win32":
            pip_executable = venv_dir / "Scripts" / "pip.exe"
        else:
            pip_executable = venv_dir / "bin" / "pip"

        try:
            # Get currently installed packages from the virtual environment.
            result = subprocess.run(
                [str(pip_executable), "freeze"],
                capture_output=True,
                text=True,
                check=True,
            )
            installed_deps_raw = result.stdout.strip().split("\n")
            installed_deps = {
                line.split("==")[0].lower().replace("_", "-"): line.split("==")[1]
                for line in installed_deps_raw
                if "==" in line
            }

            # Get declared dependencies from pyproject.toml.
            project_deps = get_project_dependencies(self.project_root)
            missing = []
            for dep in project_deps:
                # Normalize names for comparison (e.g., 'PyYAML' vs 'pyyaml').
                normalized_dep = dep.lower().replace("_", "-")
                if normalized_dep not in installed_deps:
                    missing.append(dep)

            if not missing:
                return True, ""
            return (
                False,
                f"[bold red]ERROR:[/] The following dependencies are in 'pyproject.toml' but not in 'venv': {', '.join(missing)}\n       -> [green]Suggestion:[/] Install dependencies, e.g., via 'pyinit add <dependency>' .'\n",
            )

        except (subprocess.CalledProcessError, FileNotFoundError):
            return (
                False,
                "[bold red]ERROR:[/] Could not list installed packages from 'venv'.",
            )

    def print_summary(self):
        """
        Prints the final summary report of the scan.

        Displays the overall pass/fail count and lists detailed messages for
        any issues that were found.
        """
        if self.checks_passed == self.total_checks:
            self.console.print(
                f"[bold green]\nScan[/bold green] complete. All {self.total_checks} checks passed!"
            )
        else:
            self.console.print(
                f"[bold yellow]\nScan[/bold yellow] complete. {self.checks_passed}/{self.total_checks} checks passed"
            )
            self.console.print("\n[bold yellow]Summary[/] of issues found:\n")
            for issue in self.issues:
                self.console.print(f" - {issue}")


@error_handling
def scan_project():
    """
    Performs a health check on the current project.

    This is the main entry point for the 'pyinit scan' command. It instantiates
    the ProjectScanner and runs a series of checks in a predefined order to
    evaluate the project's health.

    :raises SystemExit: If not run from within a valid project.
    """
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print(
            "[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'."
        )
        sys.exit(1)

    console.print(f"[bold green]    Scanning[/bold green] project at '{project_root}'")
    time.sleep(0.25)

    # Instantiate and run the scanner.
    scanner = ProjectScanner(console, project_root)
    scanner.run_check(
        "Project file 'pyproject.toml' validity", scanner.check_pyproject_parsable
    )
    scanner.run_check("Source directory 'src' layout", scanner.check_src_layout)
    scanner.run_check("Virtual environment 'venv' existence", scanner.check_venv_exists)
    scanner.run_check("Dependency synchronization", scanner.check_dependencies_synced)
    scanner.run_check("Git repository initialization", scanner.check_git_initialized)
    scanner.run_check(
        "Git ignore file '.gitignore' existence", scanner.check_gitignore_exists
    )
    scanner.run_check(
        "Tests directory 'tests' existence", scanner.check_tests_dir_exists
    )

    # Display the final results.
    scanner.print_summary()
