import sys
import pytest
from rich.console import Console
from pyinit.scan import ProjectScanner, scan_project

# A fixture to create a "perfect" project structure
@pytest.fixture
def perfect_project(tmp_path):
    proj = tmp_path / "perfect-proj"
    (proj / "src").mkdir(parents=True)
    (proj / "tests").mkdir()
    (proj / "venv").mkdir()
    (proj / ".git").mkdir()
    (proj / ".gitignore").touch()
    (proj / "pyproject.toml").write_text('[project]\ndependencies=["requests"]')
    (proj / "README.md").write_text("This is a test readme.")
    (proj / "requirements.txt").write_text("requests==1.2.3")
    return proj

def test_scan_perfect_project(mocker, perfect_project):
    """Tests that a perfectly configured project passes all checks."""
    # --- Arrange ---
    # Mock external commands to return successful/clean results
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.stdout = "requests==1.2.3" # Mock 'pip freeze' output
    mocker.patch("pyinit.scan.get_project_dependencies", return_value=["requests"])
    
    # --- Act ---
    scanner = ProjectScanner(Console(), perfect_project)
    scanner.check_pyproject_parsable()
    scanner.check_readme_exists()
    scanner.check_src_layout()
    scanner.check_tests_dir_exists()
    scanner.check_venv_exists()
    scanner.check_dependencies_synced()
    scanner.check_requirements_file_synced()
    scanner.check_git_initialized()
    scanner.check_git_clean_status()
    
    # --- Assert ---
    assert scanner.checks_passed == scanner.total_checks
    assert not scanner.issues

def test_scan_detects_missing_venv(mocker, perfect_project):
    """Tests that a missing venv is correctly detected."""
    # --- Arrange ---
    (perfect_project / "venv").rmdir() # Introduce the flaw
    
    # --- Act ---
    scanner = ProjectScanner(Console(), perfect_project)
    success, message = scanner.check_venv_exists()
    
    # --- Assert ---
    assert not success
    assert "venv' directory not found" in message
    
def test_scan_detects_unsynced_dependencies(mocker, perfect_project):
    """Tests detection of dependencies in pyproject.toml but not installed."""
    # --- Arrange ---
    mocker.patch("subprocess.run").return_value.stdout = "other-package==1.0.0" # only other-package is "installed"
    mocker.patch("pyinit.scan.get_project_dependencies", return_value=["requests"])
    
    # --- Act ---
    scanner = ProjectScanner(Console(), perfect_project)
    success, message = scanner.check_dependencies_synced()
    
    # --- Assert ---
    assert not success
    assert "Dependencies out of sync" in message
    assert "Missing: requests" in message

def test_scan_detects_unsynced_requirements_file(mocker, perfect_project):
    """Tests detection of a requirements.txt that doesn't match the environment."""
    # --- Arrange ---
    mocker.patch("subprocess.run").return_value.stdout = "requests==9.9.9" # Different version in venv
    
    # --- Act ---
    scanner = ProjectScanner(Console(), perfect_project)
    success, message = scanner.check_requirements_file_synced()
    
    # --- Assert ---
    assert not success
    assert "`requirements.txt` is out of sync" in message
    
def test_scan_detects_dirty_git_status(mocker, perfect_project):
    """Tests detection of an unclean Git working directory."""
    # --- Arrange ---
    # Mock the 'git status' command to return output, indicating uncommitted changes.
    mocker.patch("subprocess.run").return_value.stdout = " M README.md"
    
    # --- Act ---
    scanner = ProjectScanner(Console(), perfect_project)
    success, message = scanner.check_git_clean_status()
    
    # --- Assert ---
    assert not success
    assert "Git working directory is not clean" in message

def test_scan_project_main_function_runs(mocker, perfect_project):
    """A simple integration test to ensure the main scan_project function runs."""
    # --- Arrange ---
    mocker.patch("pyinit.scan.find_project_root", return_value=perfect_project)
    # Mock the scanner class itself to avoid re-testing all individual checks
    mock_scanner_instance = mocker.patch("pyinit.scan.ProjectScanner").return_value
    
    # --- Act ---
    scan_project()
    
    # --- Assert ---
    # Just check that the scanner was created and its methods were called
    assert mock_scanner_instance.run_check.call_count > 0
    mock_scanner_instance.print_summary.assert_called_once()