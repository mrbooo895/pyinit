import sys
from pathlib import Path
import pytest
from pyinit.create import create_project

@pytest.fixture
def mock_templates(tmp_path):
    """Creates a fake template structure within a temporary directory."""
    templates_dir = tmp_path / "templates"
    app_template_dir = templates_dir / "app" / "src" / "##PROJECT_NAME##"
    app_template_dir.mkdir(parents=True)
    
    (templates_dir / "app" / "pyproject.toml").write_text(
        'name = "##PROJECT_NAME##"\nauthors = [ { name = "##AUTHOR_NAME##" } ]'
    )
    (app_template_dir / "main.py").write_text("print('init ##PROJECT_NAME##')")
    
    return templates_dir

def test_create_project_success(mocker, tmp_path, mock_templates):
    """Tests the successful creation of a project from a template."""
    # --- Arrange ---
    project_name = "my-test-app"
    project_root = tmp_path / project_name
    
    # Mock all external interactions
    mocker.patch("pyinit.create.TEMPLATES_BASE_DIR", mock_templates)
    mocker.patch("pathlib.Path.cwd", return_value=tmp_path)
    mocker.patch("pyinit.create.get_git_config", return_value="Test Author")
    mock_subprocess_run = mocker.patch("subprocess.run")
    mock_venv_create = mocker.patch("venv.create")
    mock_console_print = mocker.patch("rich.console.Console.print")
    
    # --- Act ---
    create_project(project_name, "app")
    
    # --- Assert ---
    # 1. Check directory structure and file existence
    assert project_root.is_dir()
    assert (project_root / "pyproject.toml").is_file()
    assert (project_root / ".gitignore").is_file()
    final_src_dir = project_root / "src" / project_name
    assert final_src_dir.is_dir()
    assert (final_src_dir / "main.py").is_file()
    
    # 2. Check content replacement
    pyproject_content = (project_root / "pyproject.toml").read_text()
    assert f'name = "{project_name}"' in pyproject_content
    assert 'name = "Test Author"' in pyproject_content
    
    main_content = (final_src_dir / "main.py").read_text()
    assert f"print('init {project_name}')" in main_content
    
    # 3. Check that external commands were called correctly
    mock_venv_create.assert_called_once_with(project_root / "venv", with_pip=True)
    mock_subprocess_run.assert_called_once_with(
        ["git", "init"], cwd=project_root, check=True, capture_output=True
    )
    
    # 4. Check for final success message
    mock_console_print.assert_any_call(f"[bold green]Successfully[/bold green] created project '{project_name}'.")

def test_create_project_fails_if_folder_exists(mocker, tmp_path):
    """Tests that project creation fails if the target directory already exists."""
    # --- Arrange ---
    project_name = "existing-app"
    (tmp_path / project_name).mkdir()
    
    mocker.patch("pathlib.Path.cwd", return_value=tmp_path)
    mock_console_print = mocker.patch("rich.console.Console.print")

    # --- Act & Assert ---
    with pytest.raises(SystemExit) as excinfo:
        create_project(project_name, "app")
    
    assert excinfo.value.code == 1
    mock_console_print.assert_any_call(f"[bold red][ERROR][/bold red] Folder '{project_name}' already exists.")

def test_create_project_fails_if_template_not_found(mocker, tmp_path, mock_templates):
    """Tests that project creation fails if the requested template does not exist."""
    # --- Arrange ---
    project_name = "any-app"
    mocker.patch("pyinit.create.TEMPLATES_BASE_DIR", mock_templates)
    mocker.patch("pathlib.Path.cwd", return_value=tmp_path)
    mock_console_print = mocker.patch("rich.console.Console.print")
    
    # --- Act & Assert ---
    with pytest.raises(SystemExit) as excinfo:
        create_project(project_name, "non-existent-template")
        
    assert excinfo.value.code == 1
    mock_console_print.assert_any_call(
        f"[bold red][ERROR][/bold red] Template 'non-existent-template' not found at '{mock_templates}'."
    )