import contextlib
import subprocess

import typer
from rich.console import Console
from rich.prompt import Prompt

console = Console()


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
    after confirmation. Stop on first non-zero exit code and ask whether to continue.
    Returns 0 on full success, or the last non-zero return code.
    """
    if not commands:
        return 0

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
