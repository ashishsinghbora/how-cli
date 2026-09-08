import os
import platform
import shutil
from pathlib import Path

PACKAGE_MANAGERS: list[str] = [
    "apt",
    "dnf",
    "pacman",
    "brew",
    "nix",
    "zypper",
    "choco",
    "winget",
]

PROJECT_MARKERS: dict[str, str] = {
    "package.json": "Node.js (package.json)",
    "Cargo.toml": "Rust (Cargo.toml)",
    "pyproject.toml": "Python (pyproject.toml)",
    "go.mod": "Go (go.mod)",
    "Dockerfile": "Docker (Dockerfile)",
    ".git": "Git repository (.git)",
}


def detect_shell() -> str:
    """Detect the active shell environment."""
    if platform.system() == "Windows":
        if os.environ.get("PSModulePath") or os.environ.get(
            "PSExecutionPolicyPreference"
        ):
            return "powershell"
        return "cmd"

    shell_env = os.environ.get("SHELL", "")
    if "zsh" in shell_env:
        return "zsh"
    elif "bash" in shell_env:
        return "bash"
    elif "fish" in shell_env:
        return "fish"
    elif shell_env:
        return Path(shell_env).name

    return "bash"


def detect_package_managers() -> list[str]:
    """Detect available package managers on the system."""
    found: list[str] = []
    for pm in PACKAGE_MANAGERS:
        if shutil.which(pm):
            found.append(pm)
    return found


def detect_project_type(cwd: Path | None = None) -> list[str]:
    """Scan current directory for project type markers without inspecting contents."""
    target_dir = cwd or Path.cwd()
    detected: list[str] = []
    for marker, description in PROJECT_MARKERS.items():
        if (target_dir / marker).exists():
            detected.append(description)
    return detected


def get_environment_context(cwd: Path | None = None) -> str:
    """
    Generate a privacy-safe environment context string containing
    shell, package managers, and detected project markers.
    """
    shell = detect_shell()
    pms = detect_package_managers()
    project_types = detect_project_type(cwd)

    lines = [f"Shell: {shell}"]
    if pms:
        lines.append(f"Available Package Managers: {', '.join(pms)}")
    if project_types:
        lines.append(f"Detected Project Markers: {', '.join(project_types)}")
    else:
        lines.append("Detected Project Markers: None")

    return "\n".join(lines)
