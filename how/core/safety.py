import re
from dataclasses import dataclass


@dataclass
class RiskFlag:
    command: str
    rule_name: str
    description: str
    severity: str = "HIGH"


RULES: list[tuple[str, re.Pattern[str], str]] = [
    (
        "Fork Bomb",
        re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"),
        "Denial-of-service fork bomb that depletes system process tables.",
    ),
    (
        "Recursive Force Delete",
        re.compile(
            r"\brm\s+.*("
            r"-[a-zA-Z]*r[a-zA-Z]*f|"
            r"-[a-zA-Z]*f[a-zA-Z]*r|"
            r"(-[a-zA-Z]*r[a-zA-Z]*\s+-[a-zA-Z]*f[a-zA-Z]*)|"
            r"(-[a-zA-Z]*f[a-zA-Z]*\s+-[a-zA-Z]*r[a-zA-Z]*)|"
            r"--recursive\s+--force|"
            r"--force\s+--recursive"
            r")"
        ),
        "Permanently deletes files and directories recursively without confirmation.",
    ),
    (
        "Direct Block Device Write (dd)",
        re.compile(r"\bdd\s+.*if="),
        "Direct low-level device write that can overwrite disk partitions.",
    ),
    (
        "Format Filesystem (mkfs)",
        re.compile(r"\bmkfs(\.[a-z0-9]+)?\b"),
        "Formats storage device, destroying all existing partition data.",
    ),
    (
        "Direct Device Redirection",
        re.compile(r">\s*/dev/(sd|nvme|hd|vd)"),
        "Raw redirection to storage device that overwrites partition headers.",
    ),
    (
        "Unrestricted Permission (chmod 777)",
        re.compile(r"\bchmod\s+(-[a-zA-Z]*R[a-zA-Z]*\s+777|777\s+-[a-zA-Z]*R)"),
        "Recursively opens all read/write/execute permissions to any local user.",
    ),
    (
        "Hard Git Reset",
        re.compile(r"\bgit\s+reset\s+--hard\b"),
        "Discards uncommitted changes and overwrites tracked working tree files.",
    ),
    (
        "Force Git Push",
        re.compile(r"\bgit\s+push\s+.*(-f\b|--force\b)"),
        "Forces remote branch update, potentially overwriting shared team history.",
    ),
    (
        "Piped Shell Execution",
        re.compile(r"\b(curl|wget)\b.*\|\s*(ba|z)?sh\b"),
        "Executes unvetted remote scripts directly from the internet.",
    ),
]


def assess_risk(commands: list[str]) -> list[RiskFlag]:
    """
    Assess a list of shell commands against destructive patterns.
    Returns a list of RiskFlag objects for triggered rules.
    """
    flags: list[RiskFlag] = []
    for cmd in commands:
        cleaned = cmd.strip()
        for rule_name, pattern, description in RULES:
            if pattern.search(cleaned):
                flags.append(
                    RiskFlag(
                        command=cleaned,
                        rule_name=rule_name,
                        description=description,
                    )
                )
    return flags
