"""
pyinit - Your All-in-One Python Project Manager

"""

__version__ = "1.0.0"
from .add_module import install_module
from .build_project import install_project
from .bump_project import bump_project_version
from .clean_project import clean_project
from .dockerize_project import dockerize_project
from .env_manager import manage_env
from .format_project import format_project
from .graph_project import show_dependency_graph
from .hooks_manager import add_git_hooks
from .init_project import initialize_project
from .lint_project import lint_project
from .lock_project import lock_dependencies
from .main import main
from .new_project import create_project
from .run_project import start_project
from .scan_project import scan_project
from .test_project import run_tests
from .update_project import update_dependencies
from .venv_manager import manage_venv


__all__ = [
    "create_project",
    "initialize_project",
    "start_project",
    "install_module",
    "lock_dependencies",
    "update_dependencies",
    "install_project",
    "run_tests",
    "lint_project",
    "format_project",
    "show_dependency_graph",
    "clean_project",
    "scan_project",
    "bump_project_version",
    "manage_venv",
    "dockerize_project",
    "manage_env",
    "add_git_hooks",
    "main",
]
