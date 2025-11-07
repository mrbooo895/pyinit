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

LICENSES = {
    "mit": {
        "spdx": "MIT",
        "text": """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    },
    "gpl-3.0": {
        "spdx": "GPL-3.0-only",
        "text": """This would be the full text of the GPL-3.0 license. 
It is very long, so it's omitted here for brevity.
You should download the full text from the GNU website."""
    }
}

def list_licenses(console: Console):
    console.print("[bold green]Available licenses:[/bold green]")
    for key in LICENSES:
        console.print(f"  - {key} ({LICENSES[key]['spdx']})")

def set_license(console: Console, project_root, license_name: str):
    license_key = license_name.lower()
    if license_key not in LICENSES:
        console.print(f"[bold red][ERROR][/bold red] License '{license_name}' not recognized.")
        console.print("-> [bold green]Run[/]: 'pyinit license list' to see available options.")
        sys.exit(1)

    license_data = LICENSES[license_key]
    license_file_path = project_root / "LICENSE"

    console.print(f"[bold green]    Setting[/bold green] license to [cyan]{license_data['spdx']}[/cyan]...")
    time.sleep(0.25)
    
    if license_file_path.exists():
        confirm = console.input("[bold yellow][WARNING][/] a 'LICENSE' file already exists. Overwrite? (y/N): ")
        if confirm.lower() != 'y':
            console.print("[bold yellow][INFO][/bold yellow] Operation cancelled.")
            sys.exit(0)

    pyproject_path = project_root / "pyproject.toml"
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        
        author = data.get("project", {}).get("authors", [{"name": "Your Name"}])[0].get("name", "Your Name")
        year = time.strftime("%Y")

        license_text = license_data["text"].format(year=year, author=author)
        with open(license_file_path, "w") as f:
            f.write(license_text.strip())
        console.print(f"[bold green]     Created[/bold green] 'LICENSE' file.")
        time.sleep(1)

        data["project"]["license"] = {"text": license_data["spdx"]}
        with open(pyproject_path, "wb") as f:
            tomli_w.dump(data, f)
        console.print(f"[bold green]     Updated[/bold green] 'pyproject.toml'.")
        time.sleep(1)

    except (FileNotFoundError, tomllib.TOMLDecodeError, KeyError) as e:
        console.print(f"[bold red][ERROR][/bold red] Could not update 'pyproject.toml': {e}")
        sys.exit(1)
        
    console.print(f"\n[bold green]Successfully[/bold green] set project license to {license_data['spdx']}.")


@error_handling
def manage_license(command: str, license_name: str | None):
    console = Console()
    
    if command == "list":
        list_licenses(console)
        return

    project_root = find_project_root()
    if not project_root:
        console.print("[bold red][ERROR][/bold red] Not inside a project. Could not find 'pyproject.toml'.")
        sys.exit(1)
    
    if command == "set" and license_name:
        set_license(console, project_root, license_name)