from typing import Annotated

import typer
from rich.console import Console
from rich.prompt import Prompt

from how import __version__
from how.core.config import Config
from how.formatting import display_result

app = typer.Typer(
    name="how",
    help="An AI-based CLI assistant to help you with command line & shell.",
)
console = Console()
config = Config()


def get_version(value: bool) -> None:
    """
    Callback to get the version of the application.
    """
    if value:
        typer.echo(f"v{__version__}")
        raise typer.Exit()


@app.callback()
def show_version(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Shows the version of the application",
        callback=get_version,
    ),
) -> None:
    """
    Shows the version of the application.
    """


@app.command()
def to(
    task: Annotated[str, typer.Argument(help="The command line task to perform.")],
) -> None:
    """
    Sends the task to the LLM for analysis.
    Returns the commands to be executed in order to achieve that.
    """
    if not config.is_ready():
        typer.secho(
            "Please setup the configuration first using `how setup`",
            fg="red",
            bold=True,
        )
        raise typer.Abort()

    from how.core.exceptions import ConfigError
    from how.infer import get_result

    try:
        result = get_result(task)
    except ConfigError as e:
        typer.secho(f"Configuration error: {e}", fg="red", bold=True)
        typer.secho(
            "Please run `how setup` to configure your LLM provider.", fg="yellow"
        )
        raise typer.Abort()
    except Exception as e:  # noqa: BLE001
        typer.secho(f"Error communicating with LLM: {e}", fg="red", bold=True)
        raise typer.Abort()

    display_result(task, result)


@app.command()
def setup(
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive/--no-interactive",
            help="Whether to use interactive mode for setting up configuration.",
        ),
    ] = True,
    provider: Annotated[
        str,
        typer.Option(
            help="The LLM Provider, needs to be passed explicitly if using --no-interactive mode.",
        ),
    ] = "",
    api_key: Annotated[
        str,
        typer.Option(
            help="The API Key for the LLM provider, needs to be passed explicitly if using --no-interactive mode.",
        ),
    ] = "",
    model: Annotated[
        str,
        typer.Option(
            help="Custom model name to use (optional).",
        ),
    ] = "",
    endpoint: Annotated[
        str,
        typer.Option(
            help="Custom endpoint URL (optional, e.g. http://localhost:11434 for Ollama).",
        ),
    ] = "",
) -> None:
    """
    Sets up the configuration required to run the application.
    Set the LLM Provider & the corresponding API Key or local endpoint.
    """
    from how.core.llm import get_llm
    from how.core.providers import LLM_PROVIDERS

    if not interactive:
        if not provider:
            typer.secho(
                "Please set the --provider when using --no-interactive mode.",
                fg="red",
                bold=True,
            )
            raise typer.Abort()
        if provider not in LLM_PROVIDERS:
            typer.secho(
                f"LLM Provider '{provider}' not available. Please select from: {', '.join(LLM_PROVIDERS.keys())}",
                fg="red",
                bold=True,
            )
            raise typer.Abort()

        provider_info = LLM_PROVIDERS[provider]
        if provider_info.get("requires_key", True) and not api_key:
            typer.secho(
                f"Please provide --api-key for provider '{provider}'.",
                fg="red",
                bold=True,
            )
            raise typer.Abort()

        selected_model = model or provider_info.get("model", "")
        selected_endpoint = endpoint or provider_info.get("endpoint", "")
    else:
        provider = Prompt.ask(
            "Select the LLM Provider", choices=list(LLM_PROVIDERS.keys())
        )
        provider_info = LLM_PROVIDERS[provider]

        if provider_info.get("requires_key", True):
            api_key = Prompt.ask(f"Enter {provider} API Key", password=True)
        else:
            api_key = ""

        default_model = provider_info.get("model", "")
        selected_model = Prompt.ask("Enter model name", default=model or default_model)

        if provider == "Ollama" or provider_info.get("endpoint"):
            default_endpoint = provider_info.get("endpoint", "http://localhost:11434")
            selected_endpoint = Prompt.ask(
                "Enter endpoint URL", default=endpoint or default_endpoint
            )
        else:
            selected_endpoint = endpoint or ""

        typer.confirm("Do you want to save the configuration?", abort=True)

    # Test the provider connection before saving
    with console.status("[bold green]Testing LLM connection...[/bold green]"):
        try:
            llm = get_llm(
                provider=provider,
                api_key=api_key,
                model=selected_model or None,
                endpoint=selected_endpoint or None,
            )
            llm.invoke("Hi!")
        except Exception as e:  # noqa: BLE001
            typer.secho(
                f"Failed to connect to LLM provider '{provider}': {e}. Please check your credentials/endpoint.",
                fg="red",
                bold=True,
            )
            raise typer.Abort()

    config.setup(
        provider=provider,
        api_key=api_key,
        model=selected_model,
        endpoint=selected_endpoint,
    )
    typer.secho(
        f"Configuration saved successfully for {provider}!",
        fg="green",
        bold=True,
    )
