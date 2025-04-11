"""
CodeBook watcher module for monitoring codebook changes
"""

import os
import time
from typing import Callable
from watchfiles import watch, Change
from rich import print
from rich.panel import Panel


class CodeBookWatcher:
    """Watcher for monitoring codebook changes"""

    def __init__(self, file_path: str, on_change: Callable[[], None]):
        """Initialize the watcher

        Args:
            file_path: Path to the codebook file
            on_change: Callback function to execute when file changes
        """
        self.file_path = file_path
        self.on_change = on_change
        self.last_modified = 0

    def start(self) -> None:
        """Start watching the codebook file"""
        print(f"Starting codebook watching")

        # Print watching info
        panel = Panel(
            f"[bold green]{self.file_path}[/bold green]",
            title="Watching codebook, press [yellow]ctrl+c[/yellow] to stop",
            title_align="center",
        )
        print(panel)

        # Start watching
        for changes in watch(os.path.dirname(self.file_path)):
            for change in changes:
                change_type, path = change
                if path == self.file_path and change_type == Change.modified:
                    current_time = time.time()
                    if current_time - self.last_modified > 1:
                        self.last_modified = current_time
                        self.on_change()
