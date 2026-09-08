from pathlib import Path
from unittest.mock import patch

from how.core.history import (
    get_last_history_command,
    parse_history_line,
)


def test_parse_history_line_bash():
    assert parse_history_line("git checkout -b feature") == "git checkout -b feature"
    assert parse_history_line("#1711234567") == ""  # Bash timestamp line


def test_parse_history_line_zsh():
    assert (
        parse_history_line(": 1711234567:0;git push origin main")
        == "git push origin main"
    )
    assert (
        parse_history_line(": 12345:10;cargo build --release")
        == "cargo build --release"
    )


def test_parse_history_line_fish():
    assert (
        parse_history_line("- cmd: docker run -p 8080:80 nginx")
        == "docker run -p 8080:80 nginx"
    )


def test_get_last_history_command_ignores_how(tmp_path: Path):
    hist_file = tmp_path / ".bash_history"
    hist_file.write_text("git status\nhow to 'search text'\nls -la\nhow fix\n")

    with patch("how.core.history.get_history_file_paths", return_value=[hist_file]):
        cmd = get_last_history_command()
        assert cmd == "ls -la"


def test_get_last_history_command_nonexistent(tmp_path: Path):
    non_existent = tmp_path / "does_not_exist"
    with patch("how.core.history.get_history_file_paths", return_value=[non_existent]):
        assert get_last_history_command() is None
