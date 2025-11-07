import sys
import time

import tomli_w
from rich.console import Console

from .utils import find_project_root
from .wrappers import error_handling

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@error_handling
def bump_project_version(part: str):
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print(
            "[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'."
        )
        sys.exit(1)

    pyproject_path = project_root / "pyproject.toml"

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, FileNotFoundError):
        console.print(
            f"[bold red][ERROR][/bold red] Could not read or parse '{pyproject_path.name}'."
        )
        sys.exit(1)

    console.print("[bold green]    Bumping[/bold green] project version")
    time.sleep(0.25)

    try:
        old_version = data["project"]["version"]
        major, minor, patch = map(int, old_version.split("."))
    except (KeyError, ValueError):
        console.print(
            f"[bold red][ERROR][/bold red] Invalid or missing version string in '{pyproject_path.name}'. Expected format: 'X.Y.Z'"
        )
        sys.exit(1)
    
    else:

        if part == "major":
            major += 1
            minor = 0
            patch = 0
        elif part == "minor":
            minor += 1
            patch = 0
        elif part == "patch":
            patch += 1

        new_version = f"{major}.{minor}.{patch}"
        data["project"]["version"] = new_version

        try:
            with open(pyproject_path, "wb") as f:
                tomli_w.dump(data, f)
        except Exception as e:
            console.print(
                f"[bold red][ERROR][/bold red] Failed to write updated version to '{pyproject_path.name}': {e}"
            )
            sys.exit(1)

        console.print(
            f"[bold green]     Updating[/bold green] version from [yellow]{old_version}[/yellow] to [cyan]{new_version}[/cyan]"
        )
        console.print("\n[bold green]Successfully[/bold green] bumped project version.")
