from unittest.mock import MagicMock, patch

from how.actions import (
    copy_to_clipboard,
    execute_commands,
    interactive_action_menu,
    modify_commands,
)


def test_copy_to_clipboard_success():
    with patch("pyperclip.copy") as mock_copy:
        res = copy_to_clipboard(["echo hello", "echo world"])
        assert res is True
        mock_copy.assert_called_once_with("echo hello\necho world")


def test_copy_to_clipboard_failure():
    with patch("pyperclip.copy", side_effect=Exception("No clipboard mechanism")):
        res = copy_to_clipboard(["echo hello"])
        assert res is False


def test_execute_commands_declined():
    with patch("typer.confirm", return_value=False):
        ret = execute_commands(["ls -la"])
        assert ret == 0


def test_execute_commands_success():
    with patch("typer.confirm", return_value=True), patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        ret = execute_commands(["echo hello", "echo world"])
        assert ret == 0
        assert mock_run.call_count == 2


def test_execute_commands_failure_stop():
    with patch("typer.confirm", side_effect=[True, False]), patch(
        "subprocess.run"
    ) as mock_run:
        # First confirm is to execute, second confirm is whether to continue after failure
        mock_run.return_value = MagicMock(returncode=42)
        ret = execute_commands(["false", "echo unreachable"])
        assert ret == 42
        assert mock_run.call_count == 1


def test_modify_commands():
    with patch("builtins.input", return_value="echo edited"):
        res = modify_commands(["echo original"])
        assert res == ["echo edited"]


def test_interactive_action_menu_abort():
    with patch("rich.prompt.Prompt.ask", return_value="a"):
        # Should exit cleanly without error
        interactive_action_menu(["echo test"])


def test_interactive_action_menu_execute():
    with patch("rich.prompt.Prompt.ask", return_value="e"), patch(
        "how.actions.execute_commands"
    ) as mock_exec:
        interactive_action_menu(["echo test"])
        mock_exec.assert_called_once_with(["echo test"])
