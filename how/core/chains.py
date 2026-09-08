from typing import Any


def get_chain(llm: Any | None = None) -> Any:
    """Build and return the LangChain runnable chain using an initialized LLM."""
    from how.core.llm import get_llm
    from how.core.template import PROMPT_TEMPLATE

    if llm is None:
        llm = get_llm()

    return PROMPT_TEMPLATE | llm


def __getattr__(name: str) -> Any:
    if name == "HOW_CLI_CHAIN":
        return get_chain()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
