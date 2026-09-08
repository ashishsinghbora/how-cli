import json
import warnings
from typing import Any

from how.core.chains import get_chain
from how.core.context import get_environment_context
from how.core.parser import PARSER


def get_result(
    task: str,
    llm: Any | None = None,
    context: str | None = None,
) -> dict[str, str | list[str] | float]:
    """Invokes the chain with the given task and returns the result.

    Args:
        task (str): The task to perform.
        llm: Optional pre-instantiated LLM.
        context: Optional environment or shell context to inject.

    Returns:
        dict: The result of the chain containing commands, confidence, and status.
    """
    tries = 3
    parsed: dict[str, str | list[str] | float] = {
        "status": "error",
        "commands": [],
        "confidence": 0.0,
    }

    chain = get_chain(llm=llm)

    if context is None:
        context = get_environment_context()

    payload: dict[str, Any] = {
        "task": task,
        "context": f"Environment Context:\n{context}\n",
    }

    while tries > 0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = chain.invoke(payload)

        try:
            parsed = PARSER.invoke(res)
            break
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            tries -= 1
        except Exception:  # noqa: BLE001
            tries -= 1

    return parsed
