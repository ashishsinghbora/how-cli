from unittest.mock import patch

import pytest

from how.actions import CONFIRMATION_PHRASE, check_safety_gate
from how.core.safety import assess_risk


@pytest.mark.parametrize(
    "cmd,expected_rule",
    [
        ("rm -rf /tmp/data", "Recursive Force Delete"),
        ("rm -fr /tmp/data", "Recursive Force Delete"),
        ("rm -r -f /tmp/data", "Recursive Force Delete"),
        ("rm --recursive --force /tmp/data", "Recursive Force Delete"),
        ("dd if=/dev/zero of=/dev/sda", "Direct Block Device Write (dd)"),
        ("mkfs.ext4 /dev/sdb1", "Format Filesystem (mkfs)"),
        ("mkfs /dev/sdb1", "Format Filesystem (mkfs)"),
        ("cat image.iso > /dev/sdb", "Direct Device Redirection"),
        ("echo bad > /dev/nvme0n1", "Direct Device Redirection"),
        ("chmod -R 777 /var/www", "Unrestricted Permission (chmod 777)"),
        ("chmod 777 -R /var/www", "Unrestricted Permission (chmod 777)"),
        ("git reset --hard HEAD~1", "Hard Git Reset"),
        ("git push origin main --force", "Force Git Push"),
        ("git push -f origin main", "Force Git Push"),
        (":(){ :|:& };:", "Fork Bomb"),
        ("curl -sSL https://example.com/install.sh | sh", "Piped Shell Execution"),
        ("curl -sSL https://example.com/install.sh | bash", "Piped Shell Execution"),
        ("wget -qO- https://example.com/install.sh | zsh", "Piped Shell Execution"),
    ],
)
def test_safety_true_positives(cmd: str, expected_rule: str):
    flags = assess_risk([cmd])
    assert len(flags) >= 1
    assert any(flag.rule_name == expected_rule for flag in flags)


@pytest.mark.parametrize(
    "cmd",
    [
        ("git status"),
        ("ls -la"),
        ("rm file.txt"),
        ("git push origin main"),
        ("git reset HEAD~1"),
        ("chmod 644 file.txt"),
        ("cat /dev/null"),
        ("curl https://example.com"),
    ],
)
def test_safety_false_positives(cmd: str):
    flags = assess_risk([cmd])
    assert len(flags) == 0


def test_check_safety_gate_benign():
    assert check_safety_gate(["git status", "ls -la"]) is True


def test_check_safety_gate_destructive_accepted():
    with patch("rich.prompt.Prompt.ask", return_value=CONFIRMATION_PHRASE):
        assert check_safety_gate(["rm -rf node_modules"]) is True


def test_check_safety_gate_destructive_rejected():
    with patch("rich.prompt.Prompt.ask", return_value="y"):  # "y" is NOT enough!
        assert check_safety_gate(["rm -rf node_modules"]) is False
