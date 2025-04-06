"""
Input file plugin for managing input file functionality
"""

import os
import time
from typing import Any, Dict, Optional, Tuple, Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from autocoder.plugins import Plugin, PluginManager


class InputFileEventHandler(FileSystemEventHandler):
    """Handler for input file changes"""

    def __init__(self, plugin):
        self.plugin = plugin
        self.last_modified = 0

    def on_modified(self, event):
        if event.src_path == self.plugin.input_file_path:
            current_time = time.time()
            # Avoid multiple triggers for the same modification
            if current_time - self.last_modified > 1:
                self.last_modified = current_time
                self.plugin.run_input_file("")


class InputFilePlugin(Plugin):
    """Plugin for managing input file functionality"""

    name = "input_file"
    description = "Plugin for managing input file functionality"
    version = "0.1.0"
    input_file_path = None
    input_file_name = "autocoder_input.yaml"
    observer = None
    event_handler = None

    def __init__(
        self,
        manager: PluginManager,
        config: Optional[Dict[str, Any]] = None,
        config_path: Optional[str] = None,
    ):
        """Initialize the input file plugin"""
        super().__init__(manager, config, config_path)
        self.enabled = False

    def initialize(self) -> bool:
        """Initialize the plugin"""
        print(f"[{self.name}] Initializing input file plugin")
        project_root = self.manager.project_root()
        if not project_root:
            print(f"[{self.name}] No project root found")
            return False
        self.input_file_path = os.path.join(
            project_root, "plugins", self.id_name(), self.input_file_name
        )
        return True

    def get_commands(self) -> Dict[str, Tuple[Callable, str]]:
        """Get commands provided by this plugin"""
        return {
            "xtools/inputfile/watch": (
                self.handle_input_file,
                "Enable or disable input file watching functionality",
            ),
            "xtools/inputfile/run": (self.run_input_file, "Run the input file"),
        }

    def get_completions(self) -> Dict[str, List[str]]:
        """Get completions provided by this plugin"""
        return {
            "/xtools/inputfile/watch": ["on", "off"],
            "/xtools/inputfile/run": [],
        }

    def handle_input_file(self, args: str) -> None:
        """Handle the input file command

        Args:
            args: Command arguments (on|off)
        """
        if not args:
            print(f"[{self.name}] Please specify 'on' or 'off'")
            return

        action = args.lower()
        if action not in ["on", "off"]:
            print(f"[{self.name}] Invalid argument. Please use 'on' or 'off'")
            return

        self.enabled = action == "on"
        print(
            f"[{self.name}] Input file functionality is now {'enabled' if self.enabled else 'disabled'}"
        )
        if self.enabled:
            self.watch_input_file()
        else:
            self.stop_watching_input_file()

    def watch_input_file(self) -> None:
        """Watch the input file"""
        print(f"[{self.name}] Watching input file")
        # if the file doesn't exist, create it
        if self.input_file_path is None:
            print(f"[{self.name}] No input file path configured")
            return
        if not os.path.exists(self.input_file_path):
            self.create_input_file()

        # Start watching the file
        if self.observer is None:
            self.event_handler = InputFileEventHandler(self)
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                os.path.dirname(self.input_file_path),
                recursive=False,
            )
            self.observer.start()
            print(f"[{self.name}] Started watching file: {self.input_file_path}")

    def stop_watching_input_file(self) -> None:
        """Stop watching the input file"""
        print(f"[{self.name}] Stopping watching input file")
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.event_handler = None
            print(f"[{self.name}] Stopped watching file")

    def run_input_file(self, args: str, skip_draft: bool = True) -> None:
        """Run the input file

        Args:
            args: Command arguments (unused)
            skip_draft: Whether to skip draft files, default True
        """
        if self.input_file_path is None:
            print(f"[{self.name}] No input file path configured")
            return

        if not os.path.exists(self.input_file_path):
            print(f"[{self.name}] Input file does not exist: {self.input_file_path}")
            return

        print(f"[{self.name}] Running input file: {self.input_file_path}")
        # TODO: Implement file running logic here

    def create_input_file(self) -> None:
        """Create the input file with template content"""
        if self.input_file_path is None:
            return

        if os.path.exists(self.input_file_path):
            print(f"[{self.name}] Input file already exists: {self.input_file_path}")
            return

        # Get template file path
        template_path = os.path.join(os.path.dirname(__file__), "input_file_tpl.yaml")
        if not os.path.exists(template_path):
            print(f"[{self.name}] Template file not found: {template_path}")
            return

        # Create directory if not exists
        os.makedirs(os.path.dirname(self.input_file_path), exist_ok=True)

        # Copy template content to input file
        with open(template_path, "r") as template_file:
            template_content = template_file.read()

        with open(self.input_file_path, "w") as f:
            f.write(template_content)

        print(
            f"[{self.name}] Created input file at {self.input_file_path} using template"
        )

    def is_enabled(self) -> bool:
        """Check if the plugin is enabled"""
        return self.enabled

    def shutdown(self) -> None:
        """Shutdown the plugin"""
        print(f"[{self.name}] Shutting down input file plugin")
        self.stop_watching_input_file()
