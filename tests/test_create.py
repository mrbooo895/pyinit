import pytest

from pyinit.create import create_project


def test_create_project_success(mocker, tmp_path):
    """Tests the successful creation of a project with the simplified structure."""
    # --- Arrange ---
    project_name = "my-test-app"
    project_root = tmp_path / project_name

    # Mock all external/slow interactions
    mocker.patch("pathlib.Path.cwd", return_value=tmp_path)
    mocker.patch("pyinit.create.get_git_config", return_value="Test Author")
    mock_subprocess_run = mocker.patch("subprocess.run")
    mock_venv_create = mocker.patch("venv.create")

    # Mock the template file access via importlib.resources to return real text
    mock_template_content = (
        'name = "##PROJECT_NAME##"\nauthors = [ { name = "##AUTHOR_NAME##" } ]'
    )
    mocker.patch(
        "importlib.resources.abc.Traversable.read_text",
        return_value=mock_template_content,
    )

    # --- Act ---
    create_project(project_name)

    # --- Assert ---
    # 1. Check directory structure and file existence
    assert project_root.is_dir()
    assert (project_root / "pyproject.toml").is_file()
    assert (project_root / ".gitignore").is_file()
    assert (project_root / "README.md").is_file()
    final_src_dir = project_root / "src" / project_name
    assert final_src_dir.is_dir()
    assert (final_src_dir / "__init__.py").is_file()
    assert (final_src_dir / "main.py").is_file()
    assert (project_root / "tests" / "__init__.py").is_file()

    # 2. Check content replacement in pyproject.toml
    pyproject_content = (project_root / "pyproject.toml").read_text()
    assert f'name = "{project_name}"' in pyproject_content
    assert 'name = "Test Author"' in pyproject_content

    # 3. Check that external commands were called correctly
    mock_venv_create.assert_called_once_with(project_root / "venv", with_pip=True)
    mock_subprocess_run.assert_called_once_with(
        ["git", "init"], cwd=project_root, check=True, capture_output=True
    )


def test_create_project_fails_if_folder_exists(mocker, tmp_path):
    """Tests that project creation fails if the target directory already exists."""
    # --- Arrange ---
    project_name = "existing-app"
    (tmp_path / project_name).mkdir()

    mocker.patch("pathlib.Path.cwd", return_value=tmp_path)
    mock_console_print = mocker.patch("rich.console.Console.print")

    # --- Act & Assert ---
    with pytest.raises(SystemExit) as excinfo:
        create_project(project_name)

    assert excinfo.value.code == 1
    mock_console_print.assert_any_call(
        f"[bold red][ERROR][/bold red] Folder '{project_name}' already exists."
    )
