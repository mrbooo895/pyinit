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
from .add import add_module
from .build import build_project
from .check import check_project
from .clean import clean_project
from .docker import gen_docker_files
from .env import manage_env
from .format import format_project
from .graph import show_dependency_graph
from .info import project_info
from .init import initialize_project
from .lock import lock_dependencies
from .new import create_project
from .release import increase_version
from .run import run_project
from .scan import scan_project
from .test import run_tests
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
    # 'new' command
    parser_new = subparsers.add_parser(
        "new", help="Create a New Python Projcet Structure"
    )
    parser_new.add_argument(
        "project_name", metavar="PROJECT_NAME", help="The Name Of The New Project"
    )
    parser_new.add_argument(
        "-t",
        "--template",
        default="app",
        help="The project template to use (CLI | Library | Flask | default: app)",
    )

    # 'run' command
    subparsers.add_parser("run", help="Run Your Project's Main File")

    # 'add' command
    parser_add = subparsers.add_parser(
        "add", help="Install a Python Module/Library Into Your Project's venv"
    )
    parser_add.add_argument(
        "module_name",
        metavar="MOUDLE_NAME",
        help="Name of The Module/Library To Install",
    )

    # 'build' command
    subparsers.add_parser("build", help="Build Your Project Using Wheel")

    # 'init' command
    subparsers.add_parser(
        "init", help="Initialize a new project in an existing directory"
    )

    # 'test' command
    subparsers.add_parser("test", help="Run tests with pytest")

    # 'lock' command
    subparsers.add_parser("lock", help="Generate a requirements.txt file from the venv")

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

    # 'docker' command
    subparsers.add_parser("docker", help="Generate a Dockerfile for the project")

    # 'env' command group
    parser_env = subparsers.add_parser(
        "env", help="Manage project environment variables (.env file)"
    )
    env_subparsers = parser_env.add_subparsers(
        dest="env_command", required=True, help="env commands"
    )
    parser_env_set = env_subparsers.add_parser(
        "set", help="Set one or more environment variables"
    )
    parser_env_set.add_argument(
        "vars", nargs="+", metavar="KEY=VALUE", help="Variable(s) to set"
    )

    # 'info' command
    subparsers.add_parser("info", help="Display information about the current project")

    # --- Manual Argument Parsing for Passthrough Commands ---
    # This logic separates arguments for pyinit from arguments intended for
    # the underlying tool (e.g., pytest, ruff).
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
    # Call the appropriate function based on the parsed command.
    match args.command:
        case "new":
            create_project(args.project_name, args.template)
        case "run":
            run_project(sub_args)
        case "add":
            add_module(args.module_name)
        case "build":
            build_project()
        case "init":
            initialize_project()
        case "test":
            run_tests(sub_args)
        case "lock":
            lock_dependencies()
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
        case "docker":
            gen_docker_files()
        case "env":
            match args.env_command:
                case "set":
                    manage_env(args.vars)
        case "info":
            project_info()


# Standard boilerplate to run the main function when the script is executed.
if __name__ == "__main__":
    main()
