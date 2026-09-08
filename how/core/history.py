import os
import platform
import re
from pathlib import Path


def get_history_file_paths() -> list[Path]:
    """Return prioritized candidate history file paths for current environment."""
    candidates: list[Path] = []

    # 1. $HISTFILE if explicitly set
    histfile_env = os.environ.get("HISTFILE")
    if histfile_env:
        candidates.append(Path(histfile_env))

    home = Path.home()

    # 2. Shell-specific defaults based on $SHELL
    shell_env = os.environ.get("SHELL", "").lower()
    if "zsh" in shell_env:
        candidates.extend([home / ".zsh_history", home / ".bash_history"])
    elif "fish" in shell_env:
        candidates.append(home / ".local/share/fish/fish_history")
    else:
        candidates.extend([home / ".bash_history", home / ".zsh_history"])

    # 3. PowerShell history paths
    if platform.system() == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidates.append(
                Path(appdata)
                / "Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt"
            )
    else:
        candidates.append(
            home / ".local/share/powershell/PSReadLine/ConsoleHost_history.txt"
        )

    # Generic fallbacks
    for generic in [home / ".bash_history", home / ".zsh_history", home / ".history"]:
        if generic not in candidates:
            candidates.append(generic)

    return candidates


def parse_history_line(raw_line: str) -> str:
    """Clean shell-specific formatting (e.g., Zsh timestamp prefixes)."""
    line = raw_line.strip()
    # Zsh extended history format: ': 1698234567:0;command args'
    zsh_match = re.match(r"^:\s*\d+:\d+;(.*)$", line)
    if zsh_match:
        return zsh_match.group(1).strip()

    # Bash timestamp lines starting with #
    if line.startswith("#") and line[1:].isdigit():
        return ""

    # Fish history format: '- cmd: command args'
    if line.startswith("- cmd: "):
        return line[7:].strip()

    return line


def get_last_history_command() -> str | None:
    """
    Read the most recent command from shell history, ignoring 'how' invocations.
    Returns None if no history file exists or no valid commands found.
    """
    candidate_paths = get_history_file_paths()

    for path in candidate_paths:
        if not path.is_file():
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for raw in reversed(lines):
                cmd = parse_history_line(raw)
                if not cmd:
                    continue
                # Ignore self invocations (e.g. how fix, how to, .venv/bin/how)
                first_word = cmd.split()[0] if cmd.split() else ""
                if "how" in Path(first_word).name:
                    continue
                return cmd
        except (OSError, UnicodeDecodeError):
            continue

    return None
