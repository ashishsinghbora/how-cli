from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from how.core.config import Config
from how.core.exceptions import ConfigError
from how.core.llm import get_llm
from how.core.providers import DEFAULT_MODELS, LLM_PROVIDERS


def test_config_initialization(tmp_path: Path):
    cfg = Config(config_dir=tmp_path)
    assert cfg.config_file.exists()
    assert cfg.values == {
        "provider": "",
        "api_key": "",
        "model": "",
        "endpoint": "",
    }
    assert not cfg.is_ready()


def test_config_setup_and_is_ready(tmp_path: Path):
    cfg = Config(config_dir=tmp_path)

    # Standard provider requiring key
    cfg.setup(provider="OpenAI", api_key="sk-test", model="gpt-4o")
    assert cfg.is_ready()
    assert cfg.values["provider"] == "OpenAI"
    assert cfg.values["api_key"] == "sk-test"
    assert cfg.values["model"] == "gpt-4o"

    # Incomplete standard provider (no api key)
    cfg.setup(provider="OpenAI", api_key="")
    assert not cfg.is_ready()

    # Ollama provider does NOT require key
    cfg.setup(provider="Ollama", api_key="", endpoint="http://localhost:11434")
    assert cfg.is_ready()


def test_get_llm_unconfigured(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    with pytest.raises(ConfigError, match="Configuration is not set up"):
        get_llm()


def test_get_llm_unknown_provider():
    with pytest.raises(ConfigError, match="Unsupported or unconfigured LLM provider"):
        get_llm(provider="NonExistentProvider")


def test_get_llm_missing_key():
    with pytest.raises(ConfigError, match="API key is required"):
        get_llm(provider="OpenAI", api_key="")


def test_get_llm_ollama_instantiation():
    with patch("how.core.providers.get_provider_class") as mock_get_class:
        mock_cls = MagicMock()
        mock_get_class.return_value = mock_cls
        get_llm(
            provider="Ollama",
            model="qwen2.5-coder:latest",
            endpoint="http://localhost:11434",
        )
        mock_cls.assert_called_once_with(
            model="qwen2.5-coder:latest", base_url="http://localhost:11434"
        )


def test_provider_defaults():
    assert "Ollama" in LLM_PROVIDERS
    assert LLM_PROVIDERS["Ollama"]["requires_key"] is False
    assert LLM_PROVIDERS["OpenAI"]["requires_key"] is True
    assert DEFAULT_MODELS["Ollama"] == "qwen2.5-coder:latest"
