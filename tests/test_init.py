import sys
import pytest
from pyinit.init import initialize_project, sanitize_name

# Use parametrize for the helper function to test multiple cases easily
@pytest.mark.parametrize("input_name, expected_name", [
    ("My Awesome Project", "my_awesome_project"),
    ("project-with-dashes", "project_with_dashes"),
    ("Invalid@Symbols!", "invalidsymbols"),
])
def test_sanitize_name(input_name, expected_name):
    """Tests the name sanitization logic."""
    assert sanitize_name(input_name) == expected_name

@pytest.fixture
def mock_templates_for_init(tmp_path):
    """Creates a fake 'app' template structure."""
    templates_dir = tmp_path / "templates"
    app_template_dir = templates_dir / "app" / "src" / "##PROJECT_NAME##"
    app_template_dir.mkdir(parents=True)
    (templates_dir / "app" / "pyproject.toml").write_text('name = "##PROJECT_NAME##"')
    (app_template_dir / "main.py").touch() # Template includes a main.py
    return templates_dir

def test_initialize_project_success_with_migration(mocker, tmp_path, mock_templates_for_init):
    """Tests initializing a project with existing .py files to migrate."""
    # --- Arrange ---
    project_root = tmp_path / "Existing Script Dir"
    project_root.mkdir()
    (project_root / "app.py").write_text("print('app')")
    (project_root / "utils.py").write_text("print('utils')")
    
    # Mock all external interactions
    mocker.patch("pathlib.Path.cwd", return_value=project_root)
    mocker.patch("pyinit.init.TEMPLATES_BASE_DIR", mock_templates_for_init)
    mocker.patch("pyinit.init.get_git_config", return_value="Test User")
    mock_subprocess_run = mocker.patch("subprocess.run")
    mock_venv_create = mocker.patch("venv.create")
    
    # --- Act ---
    initialize_project()
    
    # --- Assert ---
    sanitized_name = "existing_script_dir"
    final_src_dir = project_root / "src" / sanitized_name
    
    # 1. Check that structure was created
    assert (project_root / "pyproject.toml").is_file()
    assert (project_root / ".gitignore").is_file()
    
    # 2. Check that files were migrated correctly
    assert final_src_dir.is_dir()
    assert (final_src_dir / "app.py").is_file()
    assert (final_src_dir / "utils.py").is_file()
    assert not (project_root / "app.py").exists() # Should be moved, not copied
    
    # 3. Check that template's main.py was replaced by the migrated files
    assert not (final_src_dir / "main.py").exists()

    # 4. Check external calls
    mock_subprocess_run.assert_called_once()
    mock_venv_create.assert_called_once()
    
@pytest.mark.parametrize("existing_item", ["pyproject.toml", "src", "venv"])
def test_initialize_project_fails_if_already_structured(mocker, tmp_path, existing_item):
    """Tests that init fails if the directory already contains key files/folders."""
    # --- Arrange ---
    project_root = tmp_path / "already-init-proj"
    project_root.mkdir()
    
    # Create the conflicting item (file or directory)
    if "." in existing_item:
        (project_root / existing_item).touch()
    else:
        (project_root / existing_item).mkdir()

    mocker.patch("pathlib.Path.cwd", return_value=project_root)
    mocker.patch("pyinit.init.TEMPLATES_BASE_DIR", tmp_path) # Mock template dir to pass check
    
    # --- Act & Assert ---
    with pytest.raises(SystemExit) as excinfo:
        initialize_project()
        
    assert excinfo.value.code == 1