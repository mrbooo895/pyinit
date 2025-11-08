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

from rich.console import Console

from .utils import (
    check_platform,
    check_project_root,
    find_project_root,
    get_project_dependencies,
)
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
        # Cache results to avoid running expensive commands multiple times
        self._pip_freeze_output = None

    def _get_pip_freeze(self):
        """Internal helper to get and cache the output of 'pip freeze'."""
        if self._pip_freeze_output is not None:
            return self._pip_freeze_output
        
        venv_dir = self.project_root / "venv"
        if not venv_dir.is_dir():
            return None

        pip_executable, _ = check_platform(venv_dir)
        try:
            result = subprocess.run(
                [str(pip_executable), "freeze"],
                capture_output=True, text=True, check=True
            )
            self._pip_freeze_output = result.stdout.strip()
            return self._pip_freeze_output
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def run_check(self, title, check_func):
        """Executes a single check function and reports its status."""
        self.total_checks += 1
        self.console.print(f"[bold green]     Checking[/bold green] {title}:", end="")
        success, message = check_func()
        if success:
            self.console.print(" [bold green]OK[/bold green]")
            self.checks_passed += 1
        else:
            self.console.print(" [bold red]FAIL[/bold red]")
            self.issues.append(message)

    # --- Core File Checks ---
    def check_pyproject_parsable(self):
        """Checks if `pyproject.toml` is a valid, parsable TOML file."""
        try:
            with open(self.project_root / "pyproject.toml", "rb") as f:
                tomllib.load(f)
            return True, ""
        except (tomllib.TOMLDecodeError, FileNotFoundError):
            return False, "[bold red]ERROR:[/] 'pyproject.toml' is missing or malformed."

    def check_readme_exists(self):
        """Checks for a non-empty README.md file."""
        readme_path = self.project_root / "README.md"
        if readme_path.is_file() and readme_path.stat().st_size > 10:
            return True, ""
        return False, "[bold yellow]WARNING:[/] `README.md` is missing or empty. Good documentation is key!"

    # --- Structure Checks ---
    def check_src_layout(self):
        """Checks for the presence of the standard `src/` directory."""
        if (self.project_root / "src").is_dir():
            return True, ""
        return False, "[bold yellow]WARNING:[/] Standard 'src' directory is missing."

    def check_tests_dir_exists(self):
        """Checks for the presence of a `tests/` directory, encouraging testing."""
        if (self.project_root / "tests").is_dir():
            return True, ""
        return False, "[bold yellow]INFO:[/] 'tests' directory not found. Consider adding tests."

    # --- Environment Checks ---
    def check_venv_exists(self):
        """Checks for the presence of the `venv/` virtual environment directory."""
        if (self.project_root / "venv").is_dir():
            return True, ""
        return False, "[bold red]ERROR:[/] 'venv' directory not found. Dependencies are not isolated.\n       -> [cyan]Suggestion:[/] Run 'pyinit venv create'"

    def check_dependencies_synced(self):
        """Verifies if dependencies in `pyproject.toml` are installed in the venv."""
        freeze_output = self._get_pip_freeze()
        if freeze_output is None:
            return False, "[bold red]ERROR:[/] Cannot check dependencies sync because 'venv' is missing or `pip freeze` failed."
        
        installed_deps = {line.split("==")[0].lower().replace("_", "-") for line in freeze_output.split("\n") if "==" in line}
        project_deps = get_project_dependencies(self.project_root)
        missing = [dep for dep in project_deps if dep.lower().replace("_", "-") not in installed_deps]

        if not missing:
            return True, ""
        return False, f"[bold red]ERROR:[/] Dependencies out of sync. Missing: {', '.join(missing)}\n       -> [cyan]Suggestion:[/] Run 'pyinit install ...' for the missing packages."

    def check_requirements_file_synced(self):
        """Checks if `requirements.txt` exists and matches the virtual environment."""
        requirements_path = self.project_root / "requirements.txt"
        if not requirements_path.is_file():
            return False, "[bold yellow]WARNING:[/] `requirements.txt` is missing.\n       -> [cyan]Suggestion:[/] Run 'pyinit install <any-package>' or 'pyinit uninstall <any-package>' to generate it."

        freeze_output = self._get_pip_freeze()
        if freeze_output is None:
            return False, "[bold red]ERROR:[/] Cannot check `requirements.txt` sync because 'venv' is missing."
        
        if requirements_path.read_text().strip() == freeze_output:
            return True, ""
        return False, "[bold yellow]WARNING:[/] `requirements.txt` is out of sync with the virtual environment.\n       -> [cyan]Suggestion:[/] Run 'pyinit install/uninstall' to regenerate it."

    # --- Version Control Checks ---
    def check_git_initialized(self):
        """Checks if the project directory is a Git repository."""
        if (self.project_root / ".git").is_dir():
            return True, ""
        return False, "[bold yellow]WARNING:[/] Project is not a Git repository.\n       -> [cyan]Suggestion:[/] Run 'git init'"

    def check_git_clean_status(self):
        """Checks if the Git working directory is clean (no uncommitted changes)."""
        if not (self.project_root / ".git").is_dir():
            return False, "[bold yellow]INFO:[/] Cannot check Git status (not a repository)."
        
        try:
            status_output = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root, capture_output=True, text=True, check=True
            ).stdout.strip()
            if not status_output:
                return True, ""
            return False, "[bold yellow]WARNING:[/] Git working directory is not clean (you have uncommitted changes)."
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, "[bold red]ERROR:[/] Could not get Git status."

    def print_summary(self):
        """Prints the final summary report of the scan."""
        if self.checks_passed == self.total_checks:
            self.console.print(f"[bold green]\nScan[/bold green] Complete: All {self.total_checks} checks passed! Your project is in great shape.")
        else:
            self.console.print(f"[bold yellow]\nScan[/bold yellow] Complete: {self.checks_passed}/{self.total_checks} checks passed.")
            self.console.print("\n[bold]Summary of issues and suggestions:[/bold]")
            for issue in self.issues:
                self.console.print(f"  - {issue}")


@error_handling
def scan_project():
    """Performs a health check on the current project."""
    console = Console()
    project_root = find_project_root()

    check_project_root(project_root)

    console.print(f"[bold green]    Scanning[/bold green] project at '{project_root}'\n")

    scanner = ProjectScanner(console, project_root)
    # Run all checks
    scanner.run_check("Core project file 'pyproject.toml'", scanner.check_pyproject_parsable)
    scanner.run_check("Documentation 'README.md'", scanner.check_readme_exists)
    scanner.run_check("Standard 'src' layout", scanner.check_src_layout)
    scanner.run_check("Testing folder 'tests'", scanner.check_tests_dir_exists)
    scanner.run_check("Virtual environment 'venv'", scanner.check_venv_exists)
    scanner.run_check("'pyproject.toml' vs 'venv' sync", scanner.check_dependencies_synced)
    scanner.run_check("'requirements.txt' vs 'venv' sync", scanner.check_requirements_file_synced)
    scanner.run_check("Git repository initialization", scanner.check_git_initialized)
    scanner.run_check("Git working directory status", scanner.check_git_clean_status)

    scanner.print_summary()