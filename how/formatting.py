from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from how.actions import (
    copy_to_clipboard,
    execute_commands,
    interactive_action_menu,
    modify_commands,
)

__all__ = [
    "copy_to_clipboard",
    "display_result",
    "execute_commands",
    "interactive_action_menu",
    "modify_commands",
]


def display_result(task: str, result: dict[str, Any]) -> None:
    console = Console()

    task_panel = Panel(
        Text(task, style="bold magenta"),
        title="Task",
        border_style="cyan",
        expand=False,
    )
    console.print(task_panel)

    if result.get("status") != "success":
        console.print(f"Status: [bold red]{result.get('status')}[/bold red]")
        return

    command_table = Table(box=box.ROUNDED, expand=True, show_header=False)
    command_table.add_column("Commands", style="green")
    for command in result.get("commands", []):
        command_table.add_row(str(command))

    confidence = float(result.get("confidence", 0.0))
    confidence_panel = Panel(
        f"{confidence:.2%}",
        title="Confidence Score",
        border_style="yellow",
        expand=False,
    )

    console.print(Panel(command_table, title="Commands", border_style="green"))
    console.print(confidence_panel)
