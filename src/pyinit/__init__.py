"""
pyinit - Your All-in-One Python Project Manager

"""

__version__ = "1.0.4"
from . import __version__
from .build import build_project
from .check import check_project
from .clean import clean_project
from .create import create_project
from .format import format_project
from .graph import show_dependency_graph
from .info import project_info
from .init import initialize_project
from .install import install_modules 
from .release import increase_version
from .run import run_project
from .scan import scan_project
from .test import run_tests
from .uninstall import uninstall_modules
from .update import update_modules
from .venv import manage_venv
from .wrappers import error_handling

__all__ = [
    "create_project",
    "initialize_project",
    "run_project",
    "install_modules",
    "uninstall_modules"
    "update_modules",
    "build_project",
    "run_tests",
    "check_project",
    "format_project",
    "show_dependency_graph",
    "clean_project",
    "scan_project",
    "increase_version",
    "manage_venv",
    "main",
]
