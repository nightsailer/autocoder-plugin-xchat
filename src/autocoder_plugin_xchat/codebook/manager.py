"""
CodeBook manager module for managing codebook operations
"""

import os
from typing import Optional, Callable, Dict
from .editor import CodebookEditor
from .watcher import CodebookWatcher
from .executor import CodebookExecutor
from rich import print
from rich.panel import Panel


class CodebookManager:
    """Manager for codebook operations"""

    def __init__(self, project_dir: str, on_output: Callable[[str], None]):
        """Initialize the manager

        Args:
            project_dir: Project directory path
            on_output: Callback function for output messages
        """
        self.project_dir = project_dir
        self.on_output = on_output
        self.codebook_path = os.path.join(project_dir, "codebook.yaml")
        self.editor = CodebookEditor(self.codebook_path)
        self.watcher = None
        self.executor = None

    def load_codebook(self) -> bool:
        """Load or create codebook file

        Returns:
            bool: True if successful
        """
        if not os.path.exists(self.codebook_path):
            self.editor.create_codebook()
            self.on_output(f"Created new codebook at {self.codebook_path}")

        if not self.editor.open():
            self.on_output(
                f"Please open [bold yellow]{self.codebook_path}[/bold yellow] manually"
            )
            return False

        return True

    async def start_watching(self, command_registry: Dict[str, Callable]) -> None:
        """Start watching codebook changes

        Args:
            command_registry: Dictionary of available commands
        """
        if self.watcher is not None:
            return

        self.executor = CodebookExecutor(command_registry)

        def on_change():
            self.on_output("Codebook changed, executing commands...")
            # TODO: Implement command execution logic

        self.watcher = CodebookWatcher(self.codebook_path, on_change)
        await self.watcher.start()

    def stop_watching(self) -> None:
        """Stop watching codebook changes"""
        if self.watcher is not None:
            self.watcher.stop()
            self.watcher = None
            self.on_output("Stopped watching codebook")
