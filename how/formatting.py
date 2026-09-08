from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def display_result(task: str, result: dict):
    console = Console()

    task_panel = Panel(
        Text(task, style="bold magenta"),
        title="Task",
        border_style="cyan",
        expand=False,
    )
    console.print(task_panel)

    if result["status"] != "success":
        console.print(f"Status: [bold red]{result['status']}[/bold red]")
        return

    command_table = Table(box=box.ROUNDED, expand=True, show_header=False)
    command_table.add_column("Commands", style="green")
    for command in result["commands"]:
        command_table.add_row(command)

    confidence_panel = Panel(
        f"{result['confidence']:.2%}",
        title="Confidence Score",
        border_style="yellow",
        expand=False,
    )

    console.print(Panel(command_table, title="Commands", border_style="green"))
    console.print(confidence_panel)
