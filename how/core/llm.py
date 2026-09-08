from typing import Any

from how.core.config import Config
from how.core.exceptions import ConfigError
from how.core.providers import LLM_PROVIDERS


def get_llm(
    provider: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    endpoint: str | None = None,
) -> Any:
    """
    Instantiate the chat model only when actually needed, after config validation.
    """
    if provider is None:
        config = Config()
        if not config.is_ready():
            raise ConfigError(
                "Configuration is not set up or incomplete. Please run `how setup`."
            )
        cfg_values = config.values
        provider = cfg_values.get("provider")
        api_key = api_key if api_key is not None else cfg_values.get("api_key", "")
        model = model if model is not None else (cfg_values.get("model") or None)
        endpoint = (
            endpoint if endpoint is not None else (cfg_values.get("endpoint") or None)
        )

    if not provider or provider not in LLM_PROVIDERS:
        raise ConfigError(
            f"Unsupported or unconfigured LLM provider: '{provider}'. "
            f"Please run `how setup`."
        )

    provider_info = LLM_PROVIDERS[provider]
    requires_key = provider_info.get("requires_key", True)

    if requires_key and not api_key:
        raise ConfigError(
            f"API key is required for provider '{provider}'. "
            f"Please configure it using `how setup`."
        )

    selected_model = model or provider_info.get("model")
    selected_endpoint = endpoint or provider_info.get("endpoint")

    try:
        cls = provider_info["provider"]
        if provider == "Ollama":
            kwargs: dict[str, Any] = {"model": selected_model}
            if selected_endpoint:
                kwargs["base_url"] = selected_endpoint
            return cls(**kwargs)
        elif provider == "GoogleVertexAI":
            kwargs = {"model_name": selected_model}
            if api_key:
                kwargs["api_key"] = api_key
            return cls(**kwargs)
        else:
            return cls(model=selected_model, api_key=api_key)
    except Exception as e:
        raise ConfigError(
            f"Failed to initialize LLM provider '{provider}': {e}. "
            f"Please check your settings with `how setup`."
        ) from e
