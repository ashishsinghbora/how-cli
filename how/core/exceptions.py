class HowError(Exception):
    """Base exception class for how-cli."""


class ConfigError(HowError):
    """Raised when configuration is missing, invalid, or corrupted."""
