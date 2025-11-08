import logging
import re
import sys
from pathlib import Path

from rich.logging import RichHandler


def find_project_root() -> Path | None:
    current_dir = Path.cwd().resolve()
    while current_dir != current_dir.parent:
        if (current_dir / "pyproject.toml").is_file():
            return current_dir
        current_dir = current_dir.parent
    if (current_dir / "pyproject.toml").is_file():
        return current_dir
    return None


def setup_logger():
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(show_path=False, show_level=True, show_time=False, markup=True)
        ],
    )
    log = logging.getLogger("rich")
    return log


if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def get_project_name(project_root: Path) -> str | None:
    pyproject_path = project_root / "pyproject.toml"
    try:
        with open(pyproject_path, "rb") as file:
            data = tomllib.load(file)

        return data.get("project", {}).get("name")

    except (tomllib.TOMLDecodeError, FileNotFoundError):
        return None


def get_project_dependencies(project_root: Path) -> list[str]:
    pyproject_path = project_root / "pyproject.toml"
    dependencies = []
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        if "project" in data and "dependencies" in data["project"]:
            dependencies.extend(data["project"]["dependencies"])

        if "project" in data and "optional-dependencies" in data["project"]:
            for group in data["project"]["optional-dependencies"].values():
                dependencies.extend(group)

        cleaned_deps = [
            re.split(r"[<>=!~]", dep)[0].strip() for dep in dependencies if dep.strip()
        ]
        return list(set(cleaned_deps))

    except (tomllib.TOMLDecodeError, FileNotFoundError):
        return []
