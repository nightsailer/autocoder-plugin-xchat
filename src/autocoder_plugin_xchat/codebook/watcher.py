"""
CodeBook watcher module for monitoring codebook changes
"""

import os
import time
import asyncio
from typing import Callable
from watchfiles import awatch, Change
from rich import print
from rich.panel import Panel


class CodebookWatcher:
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
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        """Start watching the codebook file asynchronously"""
        print(f"Starting codebook watching")

        # Print watching info
        panel = Panel(
            f"[bold green]{self.file_path}[/bold green]",
            title="Watching codebook, press [yellow]ctrl+c[/yellow] to stop",
            title_align="center",
        )
        print(panel)

        # Start watching
        try:
            async for changes in awatch(
                os.path.dirname(self.file_path), stop_event=self._stop_event
            ):
                for change in changes:
                    change_type, path = change
                    if path == self.file_path and change_type == Change.modified:
                        current_time = time.time()
                        if current_time - self.last_modified > 1:
                            self.last_modified = current_time
                            self.on_change()
        except asyncio.CancelledError:
            print("Codebook watching stopped")
        except Exception as e:
            print(f"Error watching codebook: {str(e)}")

    def stop(self) -> None:
        """Stop watching the codebook file"""
        self._stop_event.set()
