import os
from collections.abc import Callable
from typing import Any

os.environ["GRPC_VERBOSITY"] = "NONE"


def get_provider_class(provider: str) -> Callable[..., Any]:
    """Dynamically import and return the LLM provider class on demand."""
    if provider == "GoogleGenAI":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI
    elif provider == "GoogleVertexAI":
        from langchain_google_vertexai import ChatVertexAI

        return ChatVertexAI
    elif provider in ("GroqMistralAI", "GroqLLaMa"):
        from langchain_groq import ChatGroq

        return ChatGroq
    elif provider == "OpenAI":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI
    elif provider == "Anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic
    elif provider == "Ollama":
        try:
            from langchain_ollama import ChatOllama

            return ChatOllama
        except ImportError:
            from langchain_community.chat_models import ChatOllama

            return ChatOllama
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


class _ProviderEntry(dict):
    """Dictionary subclass that resolves the provider class lazily upon access."""

    def __init__(self, key: str, data: dict[str, Any]) -> None:
        super().__init__(data)
        self._key = key

    def __getitem__(self, item: str) -> Any:
        if item == "provider":
            return get_provider_class(self._key)
        return super().__getitem__(item)

    def get(self, item: str, default: Any = None) -> Any:
        if item == "provider":
            try:
                return get_provider_class(self._key)
            except (ImportError, AttributeError, ValueError):
                return default
        return super().get(item, default)


# Documented fallback defaults per provider
DEFAULT_MODELS: dict[str, str] = {
    "GoogleGenAI": "gemini-1.5-flash",
    "GoogleVertexAI": "gemini-1.5-flash",
    "GroqMistralAI": "mixtral-8x7b-32768",
    "GroqLLaMa": "llama3-70b-8192",
    "OpenAI": "gpt-4o",
    "Anthropic": "claude-3-5-sonnet-20240620",
    "Ollama": "qwen2.5-coder:latest",
}

LLM_PROVIDERS: dict[str, dict[str, Any]] = {
    "GoogleGenAI": _ProviderEntry(
        "GoogleGenAI",
        {"model": DEFAULT_MODELS["GoogleGenAI"], "requires_key": True},
    ),
    "GoogleVertexAI": _ProviderEntry(
        "GoogleVertexAI",
        {"model": DEFAULT_MODELS["GoogleVertexAI"], "requires_key": True},
    ),
    "GroqMistralAI": _ProviderEntry(
        "GroqMistralAI",
        {"model": DEFAULT_MODELS["GroqMistralAI"], "requires_key": True},
    ),
    "GroqLLaMa": _ProviderEntry(
        "GroqLLaMa",
        {"model": DEFAULT_MODELS["GroqLLaMa"], "requires_key": True},
    ),
    "OpenAI": _ProviderEntry(
        "OpenAI",
        {"model": DEFAULT_MODELS["OpenAI"], "requires_key": True},
    ),
    "Anthropic": _ProviderEntry(
        "Anthropic",
        {"model": DEFAULT_MODELS["Anthropic"], "requires_key": True},
    ),
    "Ollama": _ProviderEntry(
        "Ollama",
        {
            "model": DEFAULT_MODELS["Ollama"],
            "requires_key": False,
            "endpoint": "http://localhost:11434",
        },
    ),
}
