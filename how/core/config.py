import json
from pathlib import Path
from typing import Any


class Config:
    """
    Manages the configuration of the application.
    Config file is stored in ~/.how/config.json by default.
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or (Path.home() / ".how")
        self.config_file = self.config_dir / "config.json"
        self.__init_config()

    def __init_config(self) -> None:
        """
        Initialize the configuration directory & file if they don't exist.
        """
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.config_file.exists():
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "provider": "",
                        "api_key": "",
                        "model": "",
                        "endpoint": "",
                    },
                    f,
                    indent=4,
                )

    def setup(
        self,
        provider: str,
        api_key: str = "",
        model: str | None = None,
        endpoint: str | None = None,
    ) -> None:
        """
        Save the LLM Provider, API Key, and optional custom model/endpoint.
        """
        data: dict[str, Any] = {
            "provider": provider,
            "api_key": api_key,
            "model": model or "",
            "endpoint": endpoint or "",
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @property
    def values(self) -> dict[str, Any]:
        """
        Get the configuration values.
        """
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def is_ready(self) -> bool:
        """
        Check if the configuration file is ready to use.
        """
        try:
            vals = self.values
            provider = vals.get("provider")
            if not provider:
                return False

            from how.core.providers import LLM_PROVIDERS

            provider_info = LLM_PROVIDERS.get(provider)
            if not provider_info:
                return False

            requires_key = provider_info.get("requires_key", True)
            return not (requires_key and not vals.get("api_key"))
        except (KeyError, TypeError, ValueError, ImportError):
            return False
