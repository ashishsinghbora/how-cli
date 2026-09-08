from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from how.core.config import Config
from how.core.llm import get_llm
from how.core.providers import LLM_PROVIDERS
from how.how import app

runner = CliRunner()


def test_ollama_provider_metadata():
    assert "Ollama" in LLM_PROVIDERS
    ollama_info = LLM_PROVIDERS["Ollama"]
    assert ollama_info["requires_key"] is False
    assert ollama_info["endpoint"] == "http://localhost:11434"
    assert ollama_info["model"] == "qwen2.5-coder:latest"


def test_ollama_config_ready_without_key(tmp_path: Path):
    cfg = Config(config_dir=tmp_path)
    cfg.setup(
        provider="Ollama",
        api_key="",
        model="qwen2.5-coder:latest",
        endpoint="http://localhost:11434",
    )
    assert cfg.is_ready() is True


def test_ollama_get_llm():
    with patch("how.core.providers.get_provider_class") as mock_cls_getter:
        mock_chat_cls = MagicMock()
        mock_cls_getter.return_value = mock_chat_cls

        llm = get_llm(
            provider="Ollama",
            model="qwen2.5-coder:latest",
            endpoint="http://localhost:11434",
        )
        mock_chat_cls.assert_called_once_with(
            model="qwen2.5-coder:latest",
            base_url="http://localhost:11434",
        )
        assert llm == mock_chat_cls.return_value


def test_ollama_setup_cli(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    with patch("how.core.llm.get_llm") as mock_get_llm:
        mock_instance = MagicMock()
        mock_get_llm.return_value = mock_instance

        result = runner.invoke(
            app,
            [
                "setup",
                "--no-interactive",
                "--provider",
                "Ollama",
                "--endpoint",
                "http://localhost:11434",
            ],
        )
        assert result.exit_code == 0
        assert "Configuration saved successfully for Ollama" in result.output
