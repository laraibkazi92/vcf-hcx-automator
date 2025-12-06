from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.json import JSON
from rich.syntax import Syntax
import json
import yaml

class OutputFormatter:
    """Rich output formatting and visualization."""

    def __init__(self):
        self.console = Console()

    def display_table(self, data: List[Dict[str, Any]], title: str, columns: Optional[List[str]] = None):
        """Display data in a formatted table."""
        if not data:
            self.console.print(f"[yellow]No data to display for {title}[/yellow]")
            return

        if columns is None:
            columns = list(data[0].keys())

        table = Table(title=title)
        for col in columns:
            table.add_column(col.replace("_", " ").title())

        for item in data:
            row = [str(item.get(col, "")) for col in columns]
            table.add_row(*row)

        self.console.print(table)

    def display_json(self, data: Any):
        """Display data as formatted JSON."""
        self.console.print(JSON.from_data(data))

    def display_yaml(self, data: Any):
        """Display data as formatted YAML."""
        yaml_str = yaml.dump(data, sort_keys=False)
        syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=False)
        self.console.print(syntax)

    def display_error(self, message: str, details: Optional[str] = None):
        """Display an error message."""
        self.console.print(f"[bold red]Error:[/bold red] {message}")
        if details:
            self.console.print(Panel(details, title="Error Details", border_style="red"))

    def display_success(self, message: str):
        """Display a success message."""
        self.console.print(f"[bold green]Success:[/bold green] {message}")

    def display_warning(self, message: str):
        """Display a warning message."""
        self.console.print(f"[bold yellow]Warning:[/bold yellow] {message}")

    def display_info(self, message: str):
        """Display an info message."""
        self.console.print(f"[bold blue]Info:[/bold blue] {message}")

    def create_progress(self) -> Progress:
        """Create a progress bar instance."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=self.console
        )
