import argparse
import sys

from .add import add_module
from .build import build_project
from .release import increase_version
from .clean import clean_project
from .docker import gen_docker_files
from .env import manage_env
from .format import format_project
from .graph import show_dependency_graph
from .hooks import add_git_hooks
from .info import project_info
from .init import initialize_project
from .check import lint_project
from .lock import lock_dependencies
from .new import create_project
from .run import run_project
from .scan import scan_project
from .test import run_tests
from .update import update_modules
from .venv import manage_venv
from .wrappers import error_handling


@error_handling
def main():
    parser = argparse.ArgumentParser(
        description="Tool For Creating and Managing Python Projects"
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

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

    subparsers.add_parser("run", help="Run Your Project's Main File")
    parser_add = subparsers.add_parser(
        "add", help="Install a Python Module/Library Into Your Project's venv"
    )
    parser_add.add_argument(
        "module_name",
        metavar="MOUDLE_NAME",
        help="Name of The Module/Library To Install",
    )
    subparsers.add_parser(
        "build", help="Build Your Project Using Wheel"
    )
    subparsers.add_parser(
        "init", help="Initialize a new project in an existing directory"
    )
    subparsers.add_parser("test", help="Run tests with pytest")
    subparsers.add_parser("lock", help="Generate a requirements.txt file from the venv")
    subparsers.add_parser("format", help="Format the codebase with black and isort")
    parser_venv = subparsers.add_parser(
        "venv", help="Manage the project's virtual environment"
    )
    venv_subparsers = parser_venv.add_subparsers(
        dest="venv_command", required=True, help="venv commands"
    )
    venv_subparsers.add_parser("create", help="Create the virtual environment")
    venv_subparsers.add_parser("remove", help="Remove the virtual environment")
    subparsers.add_parser("check", help="check the codebase with ruff")
    subparsers.add_parser("graph", help="Display the project's dependency graph")
    subparsers.add_parser("clean", help="Remove temporary and build-related files")
    parser_release = subparsers.add_parser(
        "release", help="increment the project version (major, minor, patch)"
    )
    parser_release.add_argument(
        "part",
        choices=["major", "minor", "patch"],
        help="The part of the version to release",
    )
    parser_update = subparsers.add_parser(
        "update", help="Check for and apply modules updates"
    )
    parser_update.add_argument(
        "--upgrade", action="store_true", help="Upgrade venv modules"
    )
    subparsers.add_parser(
        "scan", help="Scan the project for configuration and structure issues"
    )
    subparsers.add_parser("dockerize", help="Generate a Dockerfile for the project")
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

    subparsers.add_parser("info", help="Display information about the current project")

    passthrough_commands = ["run", "test", "check"]
    main_args = sys.argv[1:]
    sub_args = []

    for i, arg in enumerate(main_args):
        if arg in passthrough_commands:
            sub_args = main_args[i + 1 :]
            main_args = main_args[: i + 1]
            break

    args = parser.parse_args(main_args)

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
            lint_project(sub_args)
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


if __name__ == "__main__":
    main()
