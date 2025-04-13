"""
CodeBook executor module for executing codebook commands
"""

from typing import Dict, Any, Optional, Callable
from rich import print
from rich.panel import Panel
from pydantic import BaseModel


class CodebookExecutor:
    """Executor for executing codebook commands"""

    def __init__(self, command_registry: Dict[str, Callable]):
        """Initialize the executor with a command registry

        Args:
            command_registry: Dictionary mapping command names to functions
        """
        self.command_registry = command_registry

    def run(self, cmd: str, content: str) -> bool:
        """Run a codebook command

        Args:
            cmd: Command string
            content: Content string

        Returns:
            bool: True if command executed successfully
        """
        # Get command function name
        cmd_parts = cmd.split(" ", 1)
        cmd_name = cmd_parts[0].lstrip("/")
        cmd_args = cmd_parts[1] if len(cmd_parts) > 1 else ""

        # Get command function
        cmd_fn = self.command_registry.get(cmd_name)
        if not cmd_fn:
            print(f"[red][bold]Command not found:[/bold] {cmd_name}[/red]")
            return False

        # Prepare full query
        full_query = f"{cmd_args} {content}".strip()

        # Print command info
        panel = Panel(
            f"Running command: [cyan]{full_query}[/cyan]",
            title="Running command",
            title_align="center",
        )
        print(panel)

        # Execute command
        try:
            cmd_fn(full_query)
            return True
        except Exception as e:
            print(f"[red][bold]Command execution failed:[/bold] {str(e)}[/red]")
            return False
