import sys
import pytest
from pyinit.release import increase_version

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

# This fixture creates a fake project structure for testing.
@pytest.fixture
def mock_project_for_release(tmp_path):
    def _create_project(version: str, init_content: str = None):
        project_name = "test-proj"
        project_root = tmp_path / project_name
        src_dir = project_root / "src" / project_name
        src_dir.mkdir(parents=True)

        # Create pyproject.toml
        pyproject_content = f'[project]\nname = "{project_name}"\nversion = "{version}"'
        (project_root / "pyproject.toml").write_text(pyproject_content)

        # Create __init__.py if content is provided
        if init_content is not None:
            (src_dir / "__init__.py").write_text(init_content)
        
        return project_root, project_name
    return _create_project

# Use parametrize to test all three bump parts with one function
@pytest.mark.parametrize("part, start_version, expected_version", [
    ("patch", "1.2.3", "1.2.4"),
    ("minor", "1.2.3", "1.3.0"),
    ("major", "1.2.3", "2.0.0"),
    ("patch", "0.9.11", "0.9.12"), # Test with double digits
])
def test_increase_version_success(mocker, mock_project_for_release, part, start_version, expected_version):
    """Tests successful version bumps for patch, minor, and major parts."""
    # --- Arrange ---
    init_content = f'__version__ = "{start_version}"\n# Some other content'
    project_root, project_name = mock_project_for_release(start_version, init_content)
    
    mocker.patch("pyinit.release.find_project_root", return_value=project_root)
    mock_console_print = mocker.patch("rich.console.Console.print")

    # --- Act ---
    increase_version(part)
    
    # --- Assert ---
    # 1. Check pyproject.toml
    with open(project_root / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["project"]["version"] == expected_version
    
    # 2. Check __init__.py
    init_content_after = (project_root / "src" / project_name / "__init__.py").read_text()
    assert f'__version__ = "{expected_version}"' in init_content_after
    
    # 3. Check console output
    mock_console_print.assert_any_call(
        f"[bold green]     Updating[/bold green] version from [yellow]{start_version}[/yellow] to [cyan]{expected_version}[/cyan]"
    )

def test_increase_version_fails_with_malformed_version(mocker, mock_project_for_release):
    """Tests that the function exits if the version string is not in X.Y.Z format."""
    # --- Arrange ---
    project_root, _ = mock_project_for_release("2.0-rc1", "")
    mocker.patch("pyinit.release.find_project_root", return_value=project_root)
    mock_console_print = mocker.patch("rich.console.Console.print")
    
    # --- Act & Assert ---
    with pytest.raises(SystemExit) as excinfo:
        increase_version("patch")
        
    assert excinfo.value.code == 1
    mock_console_print.assert_any_call(
        "[bold red][ERROR][/bold red] Invalid or missing version string in 'pyproject.toml'. Expected format: 'X.Y.Z'"
    )

def test_increase_version_handles_missing_init_gracefully(mocker, mock_project_for_release):
    """Tests that the command succeeds even if __init__.py is missing."""
    # --- Arrange ---
    start_version = "0.1.0"
    project_root, _ = mock_project_for_release(start_version, init_content=None) # No __init__.py
    mocker.patch("pyinit.release.find_project_root", return_value=project_root)
    
    # --- Act ---
    # We don't expect an exception here
    increase_version("patch")
    
    # --- Assert ---
    # Just check that pyproject.toml was updated
    with open(project_root / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["project"]["version"] == "0.1.1"