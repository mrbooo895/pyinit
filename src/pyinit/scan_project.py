import sys
import subprocess
import time
import re
from pathlib import Path
from rich.console import Console
from .utils import find_project_root, get_project_dependencies
from .wrappers import error_handling

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

class ProjectScanner:
    def __init__(self, console, project_root):
        self.console = console
        self.project_root = project_root
        self.checks_passed = 0
        self.total_checks = 0
        self.issues = []

    def run_check(self, title, check_func):
        self.total_checks += 1
        self.console.print(f"[bold green]     Checking[/bold green] {title}...", end="")
        time.sleep(0.15)
        success, message = check_func()
        if success:
            self.console.print(" [bold green]OK[/bold green]")
            self.checks_passed += 1
        else:
            self.console.print(" [bold red]FAIL[/bold red]")
            self.issues.append(message)

    def check_pyproject_exists(self):
        if (self.project_root / "pyproject.toml").is_file():
            return True, ""
        return False, "[bold red]FATAL:[/] 'pyproject.toml' not found. This is not a valid project."

    def check_pyproject_parsable(self):
        try:
            with open(self.project_root / "pyproject.toml", "rb") as f:
                tomllib.load(f)
            return True, ""
        except tomllib.TOMLDecodeError:
            return False, "[bold red]ERROR:[/] 'pyproject.toml' is malformed and cannot be read."

    def check_src_layout(self):
        if (self.project_root / "src").is_dir():
            return True, ""
        return False, "[bold yellow]WARNING:[/] Standard 'src' directory is missing."
        
    def check_venv_exists(self):
        if (self.project_root / "venv").is_dir():
            return True, ""
        return False, "[bold red]ERROR:[/] 'venv' directory not found. Dependencies are not isolated.\n       -> [cyan]Suggestion:[/] Run 'pyinit venv create'"
        
    def check_git_initialized(self):
        if (self.project_root / ".git").is_dir():
            return True, ""
        return False, "[bold yellow]WARNING:[/] Project is not a Git repository.\n       -> [yellow]Suggestion:[/] Run 'git init'"

    def check_gitignore_exists(self):
        if (self.project_root / ".gitignore").is_file():
            return True, ""
        return False, "[bold yellow]WARNING:[/] '.gitignore' file is missing."

    def check_tests_dir_exists(self):
        if (self.project_root / "tests").is_dir():
            return True, ""
        return False, "[bold yellow]WARNING:[/] 'tests' directory not found. Consider adding tests for your project."

    def check_dependencies_synced(self):
        venv_dir = self.project_root / "venv"
        if not venv_dir.is_dir():
            return False, "[bold red]ERROR:[/] Cannot check dependencies because 'venv' is missing."

        if sys.platform == "win32":
            pip_executable = venv_dir / "Scripts" / "pip.exe"
        else:
            pip_executable = venv_dir / "bin" / "pip"

        try:
            result = subprocess.run([str(pip_executable), "freeze"], capture_output=True, text=True, check=True)
            installed_deps_raw = result.stdout.strip().split('\n')
            installed_deps = {line.split('==')[0].lower().replace('_', '-'): line.split('==')[1] for line in installed_deps_raw if '==' in line}

            project_deps = get_project_dependencies(self.project_root)
            missing = []
            for dep in project_deps:
                normalized_dep = dep.lower().replace('_', '-')
                if normalized_dep not in installed_deps:
                    missing.append(dep)
            
            if not missing:
                return True, ""
            return False, f"[bold red]ERROR:[/] The following dependencies are in 'pyproject.toml' but not in 'venv': {', '.join(missing)}\n       -> [green]Suggestion:[/] Install dependencies, e.g., via 'pyinit add <dependency>' .'\n"
        
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, "[bold red]ERROR:[/] Could not list installed packages from 'venv'."

    def print_summary(self):
        if self.checks_passed == self.total_checks:
            self.console.print(f"[bold green]\nScan[/bold green] complete. All {self.total_checks} checks passed!")
        else:
            self.console.print(f"[bold yellow]\nScan[/bold yellow] complete. {self.checks_passed}/{self.total_checks} checks passed")
            self.console.print("\n[bold yellow]Summary[/] of issues found:\n")
            for issue in self.issues:
                self.console.print(f" - {issue}")

@error_handling
def scan_project():
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)

    console.print(f"[bold green]    Scanning[/bold green] project at '{project_root}'")
    time.sleep(0.25)
    
    scanner = ProjectScanner(console, project_root)
    scanner.run_check("Project file 'pyproject.toml' validity", scanner.check_pyproject_parsable)
    scanner.run_check("Source directory 'src' layout", scanner.check_src_layout)
    scanner.run_check("Virtual environment 'venv' existence", scanner.check_venv_exists)
    scanner.run_check("Dependency synchronization", scanner.check_dependencies_synced)
    scanner.run_check("Git repository initialization", scanner.check_git_initialized)
    scanner.run_check("Git ignore file '.gitignore' existence", scanner.check_gitignore_exists)
    scanner.run_check("Tests directory 'tests' existence", scanner.check_tests_dir_exists)
    
    scanner.print_summary()