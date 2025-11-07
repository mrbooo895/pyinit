import sys
import time
import re
from rich.console import Console
from .utils import find_project_root, get_project_name
from .wrappers import error_handling

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

def get_python_version_from_specifier(specifier: str) -> str:
    match = re.search(r'>=\s*(\d+\.\d+)', specifier)
    if match:
        return match.group(1)
    return "3.11"

@error_handling
def dockerize_project():
    console = Console()
    project_root = find_project_root()

    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)

    dockerfile_path = project_root / "Dockerfile"
    dockerignore_path = project_root / ".dockerignore"

    if dockerfile_path.exists() or dockerignore_path.exists():
        console.print("[bold yellow][WARNING][/bold yellow] Dockerfile or .dockerignore already exists.")
        confirm = console.input("Do you want to overwrite them? (y/N): ")
        if confirm.lower() != 'y':
            console.print("[bold yellow][INFO][/bold yellow] Operation cancelled by user")
            sys.exit(0)
    
    console.print(f"[bold green]    Generating[/bold green] Docker configuration files...")
    time.sleep(1)
    
    project_name = get_project_name(project_root) or "app"
    pyproject_path = project_root / "pyproject.toml"
    python_version = "3.11"
    
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        python_specifier = data.get("project", {}).get("requires-python", ">=3.11")
        python_version = get_python_version_from_specifier(python_specifier)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        console.print("[dim yellow][WARNING][/dim yellow] Could not read 'pyproject.toml' for Python version. Defaulting to 3.11.")

    dockerfile_content = f"""
# ---- Builder Stage ----
# Use an official Python runtime as a parent image
FROM python:{python_version}-slim as builder

# Set the working directory
WORKDIR /app

# Install build dependencies
RUN pip install --upgrade pip
RUN pip install build

# Copy project definition and build the wheel
COPY pyproject.toml .
RUN python -m build

# ---- Runner Stage ----
# Use a slim, official Python runtime as the final image
FROM python:{python_version}-slim

# Set the working directory
WORKDIR /app

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Copy the built wheel from the builder stage
COPY --from=builder /app/dist/*.whl .

# Install the wheel
RUN pip install *.whl

# Copy the application source code (optional, useful if app reads data files)
COPY src/{project_name} ./src/{project_name}

# Command to run the application
# Note: You might need to change this command based on your project's entry point
CMD ["python", "-m", "{project_name}.main"]
"""

    dockerignore_content = """
# Git
.git
.gitignore

# Docker
Dockerfile
.dockerignore

# Python virtual environment
venv/
.venv/

# Python cache
__pycache__/
*.pyc

# Build artifacts
dist/
build/
*.egg-info/

# IDE and OS files
.idea/
.vscode/
.DS_Store
"""

    try:
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content.strip())
        console.print(f"[bold green]     Created[/bold green] 'Dockerfile' using Python {python_version}")
        time.sleep(1)
        
        with open(dockerignore_path, "w") as f:
            f.write(dockerignore_content.strip())
        console.print(f"[bold green]     Created[/bold green] '.dockerignore'")
        time.sleep(1)

        console.print("\n[bold green]Successfully[/bold green] generated Docker files.")
        console.print(f"-> [cyan]Suggestion:[/] You can now build your image with: 'docker build -t {project_name}'.")
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] Failed to write Docker files: {e}")
        sys.exit(1)