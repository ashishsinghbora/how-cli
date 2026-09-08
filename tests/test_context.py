from pathlib import Path
from unittest.mock import patch

from how.core.context import (
    detect_package_managers,
    detect_project_type,
    detect_shell,
    get_environment_context,
)


def test_detect_project_nodejs(tmp_path: Path):
    (tmp_path / "package.json").write_text('{"name": "test-pkg"}')
    detected = detect_project_type(tmp_path)
    assert any("Node.js" in d for d in detected)


def test_detect_project_rust(tmp_path: Path):
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "test-cargo"')
    detected = detect_project_type(tmp_path)
    assert any("Rust" in d for d in detected)


def test_detect_project_python(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test-py"')
    detected = detect_project_type(tmp_path)
    assert any("Python" in d for d in detected)


def test_detect_project_no_markers(tmp_path: Path):
    detected = detect_project_type(tmp_path)
    assert detected == []
    context = get_environment_context(tmp_path)
    assert "Detected Project Markers: None" in context


def test_detect_shell_unix():
    with patch.dict("os.environ", {"SHELL": "/bin/zsh"}):
        assert detect_shell() == "zsh"

    with patch.dict("os.environ", {"SHELL": "/usr/bin/bash"}):
        assert detect_shell() == "bash"

    with patch.dict("os.environ", {"SHELL": "/usr/bin/fish"}):
        assert detect_shell() == "fish"


def test_detect_package_managers():
    with patch("shutil.which") as mock_which:
        mock_which.side_effect = lambda pm: (
            f"/usr/bin/{pm}" if pm in ["apt", "brew"] else None
        )
        found = detect_package_managers()
        assert found == ["apt", "brew"]


def test_get_environment_context_privacy(tmp_path: Path):
    secret_file = tmp_path / "package.json"
    secret_file.write_text('{"secret_key": "SUPER_SECRET_TOKEN_DO_NOT_LEAK"}')
    context = get_environment_context(tmp_path)

    assert "SUPER_SECRET_TOKEN_DO_NOT_LEAK" not in context
    assert "Node.js (package.json)" in context
    assert "Shell:" in context
