# Copyright (c) 2025 mrbooo895.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Main entry point for the pyinit command-line tool.

This module is responsible for parsing command-line arguments, setting up the
main parser and its subparsers for each command, and dispatching to the
appropriate function based on the user's input.
"""

import argparse
import sys

# Import handler functions for each command from their respective modules.
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


@error_handling
def main():
    """
    Parses arguments and executes the corresponding pyinit command.
    """
    # --- Main Parser Setup ---
    parser = argparse.ArgumentParser(
        description="Tool For Creating and Managing Python Projects"
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # --- Command Definitions ---
    # 'create'
    parser_create = subparsers.add_parser(
        "create", help="Create a New Python Projcet Structure"
    )
    parser_create.add_argument(
        "project_name", metavar="PROJECT_NAME", help="The Name Of The New Project"
    )
    parser_create.add_argument(
        "-t",
        "--template",
        default="app",
        help="The project template to use (CLI | Library | Flask | default: app)",
    )

    # '--version' command
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program's version number and exit",
    )

    # 'run' command
    subparsers.add_parser("run", help="Run Your Project's Main File")

    # 'install' command
    parser_install = subparsers.add_parser(
        "install", help="Install Python packages and update requirements.txt"
    )
    parser_install.add_argument(
        "modules",
        nargs="+",
        metavar="PACKAGE",
        help="One or more packages to install",
    )

    # 'uninstall'
    parser_uninstall = subparsers.add_parser(
        "uninstall", help="Uninstall Python packages and update requirements.txt"
    )
    parser_uninstall.add_argument(
        "modules",
        nargs="+",
        metavar="PACKAGE",
        help="One or more packages to uninstall",
    )

    # 'build' command
    subparsers.add_parser("build", help="Build Your Project Using Wheel")

    # 'init' command
    subparsers.add_parser(
        "init", help="Initialize a new project in an existing directory"
    )

    # 'test' command
    subparsers.add_parser("test", help="Run tests with pytest")

    # 'lock' command (Removed)
    # The 'lock' functionality is now integrated into 'install' and 'uninstall'.

    # 'format' command
    subparsers.add_parser("format", help="Format the codebase with black and isort")

    # 'venv' command group
    parser_venv = subparsers.add_parser(
        "venv", help="Manage the project's virtual environment"
    )
    venv_subparsers = parser_venv.add_subparsers(
        dest="venv_command", required=True, help="venv commands"
    )
    venv_subparsers.add_parser("create", help="Create the virtual environment")
    venv_subparsers.add_parser("remove", help="Remove the virtual environment")

    # 'check' command
    subparsers.add_parser("check", help="check the codebase with ruff")

    # 'graph' command
    subparsers.add_parser("graph", help="Display the project's dependency graph")

    # 'clean' command
    subparsers.add_parser("clean", help="Remove temporary and build-related files")

    # 'release' command
    parser_release = subparsers.add_parser(
        "release", help="increment the project version (major, minor, patch)"
    )
    parser_release.add_argument(
        "part",
        choices=["major", "minor", "patch"],
        help="The part of the version to release",
    )

    # 'update' command
    parser_update = subparsers.add_parser(
        "update", help="Check for and apply modules updates"
    )
    parser_update.add_argument(
        "--upgrade", action="store_true", help="Upgrade venv modules"
    )

    # 'scan' command
    subparsers.add_parser(
        "scan", help="Scan the project for configuration and structure issues"
    )

    # 'info' command
    subparsers.add_parser("info", help="Display information about the current project")

    # --- Manual Argument Parsing for Passthrough Commands ---
    passthrough_commands = ["run", "test", "check"]
    main_args = sys.argv[1:]
    sub_args = []

    for i, arg in enumerate(main_args):
        if arg in passthrough_commands:
            sub_args = main_args[i + 1 :]
            main_args = main_args[: i + 1]
            break

    args = parser.parse_args(main_args)

    # --- Command Dispatching ---
    match args.command:
        case "create":
            create_project(args.project_name, args.template)
        case "run":
            run_project(sub_args)
        case "install":
            install_modules(args.modules)
        case "uninstall":
            uninstall_modules(args.modules)
        case "build":
            build_project()
        case "init":
            initialize_project()
        case "test":
            run_tests(sub_args)
        case "format":
            format_project()
        case "venv":
            manage_venv(args.venv_command)
        case "check":
            check_project(sub_args)
        case "graph":
            show_dependency_graph()
        case "clean":
            clean_project()
        case "release":
            increase_version(args.part)
        case "update":
            update_modules(args.upgrade)
        case "scan":
            scan_project()
        case "info":
            project_info()


if __name__ == "__main__":
    main()
