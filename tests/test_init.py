import pytest

from pyinit.init import initialize_project, sanitize_name


@pytest.mark.parametrize(
    "input_name, expected_name",
    [
        ("My Awesome Project", "my_awesome_project"),
        ("project-with-dashes", "project_with_dashes"),
    ],
)
def test_sanitize_name(input_name, expected_name):
    """Tests the name sanitization logic."""
    assert sanitize_name(input_name) == expected_name


def test_initialize_project_success_with_migration(mocker, tmp_path):
    """Tests initializing a project with existing .py files to migrate."""
    # --- Arrange ---
    project_root = tmp_path / "Existing Script Dir"
    project_root.mkdir()
    (project_root / "app.py").write_text("print('app')")
    (project_root / "main.py").write_text(
        "print('main')"
    )  # Include a main.py to test it's preserved

    # Mock all external and slow interactions
    mocker.patch("pathlib.Path.cwd", return_value=project_root)
    mocker.patch("pyinit.init.get_git_config", return_value="Test User")
    mock_subprocess_run = mocker.patch("subprocess.run")
    mock_venv_create = mocker.patch("venv.create")

    # Mock the internal template file access to return real text
    mock_template_content = 'name = "##PROJECT_NAME##"'
    mocker.patch(
        "importlib.resources.abc.Traversable.read_text",
        return_value=mock_template_content,
    )

    # --- Act ---
    initialize_project()

    # --- Assert ---
    sanitized_name = "existing_script_dir"
    final_src_dir = project_root / "src" / sanitized_name

    # 1. Check that structure was created
    assert (project_root / "pyproject.toml").is_file()
    assert (project_root / "tests").is_dir()
    assert (project_root / "README.md").is_file()

    # 2. Check that files were migrated correctly
    assert final_src_dir.is_dir()
    assert (final_src_dir / "app.py").is_file()
    assert (final_src_dir / "main.py").is_file()  # Migrated main.py should exist
    assert not (project_root / "app.py").exists()  # Original should be gone

    # 3. Check external calls
    mock_subprocess_run.assert_called_once()
    mock_venv_create.assert_called_once()


def test_initialize_project_creates_main_if_missing(mocker, tmp_path):
    """Tests that a default main.py is created if not present in migrated files."""
    # --- Arrange ---
    project_root = tmp_path / "no-main-project"
    project_root.mkdir()
    (project_root / "other.py").touch()  # A file exists, but not main.py

    mocker.patch("pathlib.Path.cwd", return_value=project_root)
    mocker.patch("pyinit.init.get_git_config", return_value="Test User")
    mocker.patch("subprocess.run")
    mocker.patch("venv.create")

    # Mock the internal template to return empty content
    mocker.patch("importlib.resources.abc.Traversable.read_text", return_value="")

    # --- Act ---
    initialize_project()

    # --- Assert ---
    final_src_dir = project_root / "src" / "no_main_project"
    assert (final_src_dir / "main.py").is_file()  # Default main.py should be created
    assert (final_src_dir / "other.py").is_file()  # Migrated file should also exist


@pytest.mark.parametrize("existing_item", ["pyproject.toml", "src", "venv"])
def test_initialize_project_fails_if_already_structured(
    mocker, tmp_path, existing_item
):
    """Tests that init fails if the directory already contains key files/folders."""
    # --- Arrange ---
    project_root = tmp_path / "already-init-proj"
    project_root.mkdir()

    if "." in existing_item:
        (project_root / existing_item).touch()
    else:
        (project_root / existing_item).mkdir()

    mocker.patch("pathlib.Path.cwd", return_value=project_root)

    # --- Act & Assert ---
    with pytest.raises(SystemExit) as excinfo:
        initialize_project()

    assert excinfo.value.code == 1
