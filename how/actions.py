import contextlib
import subprocess

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from how.core.safety import assess_risk

console = Console()

CONFIRMATION_PHRASE = "I UNDERSTAND THE RISKS"


def check_safety_gate(commands: list[str]) -> bool:
    """
    Check if commands contain destructive patterns. If so, display a bold
    warning panel and require an exact confirmation phrase.
    """
    flags = assess_risk(commands)
    if not flags:
        return True

    warning_text = "[bold red]WARNING: Destructive or High-Risk Command(s) Detected![/bold red]\n\n"
    for flag in flags:
        warning_text += (
            f"• [bold yellow]{flag.rule_name}[/bold yellow]: [bold white]{flag.command}[/bold white]\n"
            f"  {flag.description}\n"
        )
    warning_text += (
        f"\nTo prevent accidental damage, type the exact confirmation phrase:\n"
        f"[bold white]{CONFIRMATION_PHRASE}[/bold white]"
    )

    console.print(
        Panel(
            warning_text,
            title="[bold red]SAFETY GUARDRAIL ALERT[/bold red]",
            border_style="red",
        )
    )

    try:
        user_input = Prompt.ask("Confirmation phrase")
        if user_input.strip() != CONFIRMATION_PHRASE:
            console.print(
                "[yellow]Confirmation phrase mismatch. Execution blocked.[/yellow]"
            )
            return False
        return True
    except KeyboardInterrupt:
        console.print("\n[yellow]Execution blocked.[/yellow]")
        return False


def copy_to_clipboard(commands: list[str]) -> bool:
    """Copy commands to clipboard via pyperclip."""
    joined = "\n".join(commands)
    try:
        import pyperclip

        pyperclip.copy(joined)
        console.print("[bold green]✓ Commands copied to clipboard![/bold green]")
        return True
    except Exception as e:  # noqa: BLE001
        console.print(
            f"[yellow]! Clipboard copy failed: {e}. "
            "Please ensure xclip, xsel, or wl-clipboard is installed.[/yellow]"
        )
        return False


def execute_commands(commands: list[str]) -> int:
    """
    Run commands sequentially via subprocess.run(cmd, shell=True)
    after confirmation and safety verification.
    """
    if not commands:
        return 0

    if not check_safety_gate(commands):
        return 1

    if not typer.confirm("Are you sure you want to execute these commands?"):
        console.print("[yellow]Execution cancelled.[/yellow]")
        return 0

    for idx, cmd in enumerate(commands, start=1):
        console.print(f"\n[bold cyan]({idx}/{len(commands)}) $ {cmd}[/bold cyan]")
        try:
            proc = subprocess.run(cmd, shell=True, check=False)
            if proc.returncode != 0:
                console.print(
                    f"[bold red]Command failed with exit code {proc.returncode}[/bold red]"
                )
                if idx < len(commands):
                    continue_run = typer.confirm(
                        "Do you want to continue running the remaining commands?",
                        default=False,
                    )
                    if not continue_run:
                        console.print("[yellow]Execution stopped.[/yellow]")
                        return proc.returncode
                else:
                    return proc.returncode
            else:
                console.print("[green]✓ Success (exit code 0)[/green]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Execution interrupted by user.[/yellow]")
            return 130
        except OSError as e:
            console.print(f"[bold red]Error executing command: {e}[/bold red]")
            return 1

    return 0


def modify_commands(commands: list[str]) -> list[str]:
    """Allow inline editing of the commands."""
    joined = "\n".join(commands)
    console.print("[cyan]Modify the command below:[/cyan]")
    try:
        import readline

        def hook() -> None:
            readline.insert_text(joined)
            readline.set_startup_hook()

        readline.set_startup_hook(hook)
        edited = input("> ")
    except Exception:  # noqa: BLE001
        edited = Prompt.ask("Edit command", default=joined)
    finally:
        with contextlib.suppress(Exception):
            import readline

            readline.set_startup_hook(None)

    new_cmds = [line.strip() for line in edited.splitlines() if line.strip()]
    if new_cmds:
        return new_cmds
    return commands


def interactive_action_menu(commands: list[str]) -> None:
    """Interactive action menu offering Execute, Copy, Modify, and Abort."""
    current_commands = list(commands)
    if not current_commands:
        return

    while True:
        try:
            console.print(
                "\n[bold]Options:[/bold] "
                "[bold green][E]xecute[/bold green] | "
                "[bold cyan][C]opy[/bold cyan] | "
                "[bold yellow][M]odify[/bold yellow] | "
                "[bold red][A]bort[/bold red]"
            )
            choice = Prompt.ask(
                "Select an action",
                choices=["e", "c", "m", "a", "E", "C", "M", "A"],
                default="a",
            ).lower()

            if choice == "e":
                execute_commands(current_commands)
                break
            elif choice == "c":
                copy_to_clipboard(current_commands)
            elif choice == "m":
                current_commands = modify_commands(current_commands)
                console.print(
                    f"[green]Updated command(s):[/green] {', '.join(current_commands)}"
                )
            elif choice == "a":
                console.print("[yellow]Aborted.[/yellow]")
                break
        except KeyboardInterrupt:
            console.print("\n[yellow]Aborted.[/yellow]")
            break
