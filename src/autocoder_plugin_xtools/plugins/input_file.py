"""
Input file plugin for managing input file functionality
"""

import os
import time
from typing import Any, Dict, Optional, Tuple, Callable, List
from watchfiles import watch, Change
import threading
import yaml
from autocoder.plugins import Plugin, PluginManager


class InputFilePlugin(Plugin):
    """Plugin for managing input file functionality"""

    name = "xtools_input_file"
    description = "Plugin for managing input file functionality"
    version = "0.1.0"
    input_file_path = None
    input_file_name = "autocoder_input.yaml"
    last_modified = 0

    def __init__(
        self,
        manager: PluginManager,
        config: Optional[Dict[str, Any]] = None,
        config_path: Optional[str] = None,
    ):
        """Initialize the input file plugin"""
        super().__init__(manager, config, config_path)

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
                self.watch_input_file,
                "Start watching the input file",
            ),
            "xtools/inputfile/run": (self.run_input_file, "Run the input file"),
        }

    def get_completions(self) -> Dict[str, List[str]]:
        """Get completions provided by this plugin"""
        return {
            "/xtools/inputfile/watch": [],
            "/xtools/inputfile/run": [],
        }

    def watch_input_file(self, args: str = "") -> None:
        """Watch the input file

        Args:
            args: Command arguments (unused)
        """
        print(f"[{self.name}] Starting input file watching")
        # if the file doesn't exist, create it
        if self.input_file_path is None:
            print(f"[{self.name}] No input file path configured")
            return
        if not os.path.exists(self.input_file_path):
            self.create_input_file()

        if not os.path.exists(self.input_file_path):
            print(f"[{self.name}] Input file creation failed: {self.input_file_path}")
            return
        # print the input file path to the console
        print(f"[{self.name}] Input file path: {self.input_file_path}")

        # Check if running in Cursor environment
        is_cursor = "CURSOR_TRACE_ID" in os.environ
        try:
            import subprocess

            if is_cursor:
                subprocess.run(["cursor", self.input_file_path], check=False)
                print(f"[{self.name}] Opened input file in Cursor")
            else:
                print(f"Please open [{self.name}] to edit the input file")
        except Exception as e:
            print(f"[{self.name}] Failed to open file in editor: {str(e)}")

        # Start watching the file synchronously
        print(f"[{self.name}] Started watching file: {self.input_file_path}")
        for changes in watch(os.path.dirname(self.input_file_path)):
            for change in changes:
                change_type, path = change
                if path == self.input_file_path and change_type == Change.modified:
                    current_time = time.time()
                    if current_time - self.last_modified > 1:
                        self.last_modified = current_time
                        self.run_input_file(skip_draft=True)

    def open_in_cursor(self) -> None:
        """Open the input file in Cursor"""
        if self.input_file_path is None:
            print(f"[{self.name}] No input file path configured")
            return
        try:
            import subprocess

            subprocess.run(["cursor", self.input_file_path], check=False)
            print(f"[{self.name}] Opened input file in Cursor")
        except Exception as e:
            print(f"[{self.name}] Failed to open file in editor: {str(e)}")

    def run_input_file(self, skip_draft: bool = False) -> None:
        """Run the input file

        Args:
            skip_draft: Whether to skip draft files, default True
        """
        if self.input_file_path is None:
            print(f"[{self.name}] No input file path configured")
            return

        if not os.path.exists(self.input_file_path):
            print(f"[{self.name}] Input file does not exist: {self.input_file_path}")
            return

        print(f"[{self.name}] Running input file: {self.input_file_path}")
        # load the input file (yaml)
        with open(self.input_file_path, "r") as f:
            input_file_data = yaml.safe_load(f)
        print(input_file_data)
        # get cmd from input_file
        cmd = input_file_data.get("cmd")
        if not cmd:
            return

        print(f"Running command: {cmd}")

        # get first part of cmd, split by space
        cmd_fn_name = cmd.split(" ")[0]
        if not cmd_fn_name:
            return
        # get rid of cmd as extras, subcommand and query
        cmd_extras = cmd[len(cmd_fn_name) :]
        cmd_fn_name = cmd_fn_name.lstrip("/")
        if not cmd_fn_name:
            return

        # get the wrapped function
        wrapped_fn = self.manager.get_wrapped_function(cmd_fn_name)
        if not wrapped_fn:
            return
        # full query
        full_query = cmd_extras + " " + input_file_data.get("content", "")
        # run the wrapped function
        wrapped_fn(full_query)

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

    def shutdown(self) -> None:
        """Shutdown the plugin"""
        print(f"[{self.name}] Shutting down input file plugin")
