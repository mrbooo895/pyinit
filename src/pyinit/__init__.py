"""
pyinit - Your All-in-One Python Project Manager

"""

__version__ = "1.0.1"
from .add import add_module
from .build import build_project
from .check import lint_project
from .clean import clean_project
from .docker import gen_docker_files
from .env import manage_env
from .format import format_project
from .init import initialize_project
from .main import main
from .new import create_project
from .release import increase_version
from .run import run_project
from .scan import scan_project
from .test import run_tests
from .update import update_modules
from .venv import manage_venv

__all__ = [
    "create_project",
    "initialize_project",
    "run_project",
    "add_module",
    "lock_dependencies",
    "update_modules",
    "build_project",
    "run_tests",
    "lint_project",
    "format_project",
    "show_dependency_graph",
    "clean_project",
    "scan_project",
    "increase_version",
    "manage_venv",
    "gen_docker_files",
    "manage_env",
    "add_git_hooks",
    "main",
]
