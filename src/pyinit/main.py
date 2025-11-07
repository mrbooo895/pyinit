import argparse
import sys

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
from .new_project import create_project
from .run_project import start_project
from .scan_project import scan_project
from .test_project import run_tests
from .update_project import update_dependencies
from .venv_manager import manage_venv
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
        help="The project template to use (default: app)",
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
        "build", help="Build Your Project and install it into the system"
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
    subparsers.add_parser("lint", help="Lint the codebase with ruff")
    subparsers.add_parser("graph", help="Display the project's dependency graph")
    subparsers.add_parser("clean", help="Remove temporary and build-related files")
    parser_bump = subparsers.add_parser(
        "bump", help="Increment the project version (major, minor, patch)"
    )
    parser_bump.add_argument(
        "part",
        choices=["major", "minor", "patch"],
        help="The part of the version to bump",
    )
    parser_update = subparsers.add_parser(
        "update", help="Check for and apply dependency updates"
    )
    parser_update.add_argument(
        "--upgrade", action="store_true", help="Upgrade outdated packages"
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
    subparsers.add_parser("add-hooks", help="Set up pre-commit hooks for the project")

    passthrough_commands = ["run", "test", "lint"]
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
            start_project(sub_args)
        case "add":
            install_module(args.module_name)
        case "build":
            install_project()
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
        case "lint":
            lint_project(sub_args)
        case "graph":
            show_dependency_graph()
        case "clean":
            clean_project()
        case "bump":
            bump_project_version(args.part)
        case "update":
            update_dependencies(args.upgrade)
        case "scan":
            scan_project()
        case "dockerize":
            dockerize_project()
        case "env":
            match args.env_command:
                case "set":
                    manage_env(args.vars)
        case "add-hooks":
            add_git_hooks()


if __name__ == "__main__":
    main()
