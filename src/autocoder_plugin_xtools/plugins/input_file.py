"""
Input file plugin for managing input file functionality
"""

import os
import time
from typing import Any, Dict, Optional, Tuple, Callable, List
from watchfiles import watch, Change
import threading
import yaml
from rich import print
from rich.panel import Panel
from autocoder.plugins import Plugin, PluginManager
from autocoder_plugin_xtools.plugins.utils import (
    is_cursor_environment,
    is_vscode_environment,
    is_jetbrains_environment,
)

from autocoder.auto_coder_runner import (
    configure,
    mcp,
    manage_models,
    gen_and_exec_shell_command,
)
from autocoder.events.event_manager_singleton import gengerate_event_file_path


class InputFilePlugin(Plugin):
    """Plugin for managing input file functionality"""

    name = "xtools_input_file"
    description = "Plugin for managing input file functionality"
    version = "0.1.0"
    input_file_path = None
    input_file_name = "autocoder_input.yaml"
    last_modified = 0
    supported_commands: Dict[str, Callable] = {}
    with_event_commands = [
        "chat",
        "coding",
        "auto",
    ]

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
        self.supported_commands.update(self.manager.get_wrapped_functions())
        self.supported_commands.update(
            {
                "conf": configure,
                "auto": self.supported_commands["auto_command"],  # alias
                "mcp": mcp,
                "models": manage_models,
            }
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
            print(
                f"[{self.name}] Input file creation failed: [red]{self.input_file_path}[/red]"
            )
            return
        # print the input file path to the console
        print(
            f"[{self.name}] Input file path: [bold cyan]{self.input_file_path}[/bold cyan]"
        )

        if is_cursor_environment():
            ok = self.open_in_cursor()
            if not ok:
                print(
                    f"[{self.name}] Please open [bold yellow]{self.input_file_path}[/bold yellow] to edit"
                )
        elif is_vscode_environment():
            ok = self.open_in_vscode()
            if not ok:
                print(
                    f"[{self.name}] Please open [bold yellow]{self.input_file_path}[/bold yellow] to edit"
                )
        elif is_jetbrains_environment():
            ok = self.open_in_jetbrains()
            if not ok:
                print(
                    f"[{self.name}] Please open [bold yellow]{self.input_file_path}[/bold yellow] to edit"
                )
        else:
            print(
                f"[{self.name}] Please open [bold yellow]{self.input_file_path}[/bold yellow] to edit"
            )

        # print panel with title "Watching file" and self.input_file_path
        panel = Panel(
            f"[bold green]{self.input_file_path}[/bold green]",
            title="Watching input file, press [yellow]ctrl+c[/yellow] to stop",
            title_align="center",
        )
        print(panel)

        for changes in watch(os.path.dirname(self.input_file_path)):
            for change in changes:
                change_type, path = change
                if path == self.input_file_path and change_type == Change.modified:
                    current_time = time.time()
                    if current_time - self.last_modified > 1:
                        self.last_modified = current_time
                        self.run_input_file(skip_draft=True)

    def open_in_cursor(self) -> bool:
        """Open the input file in Cursor"""
        if self.input_file_path is None:
            print(f"[{self.name}] No input file path configured")
            return False
        try:
            import subprocess

            subprocess.run(["cursor", self.input_file_path], check=False)
            print(f"[{self.name}] Opened input file in Cursor")
            return True
        except Exception as e:
            print(f"[{self.name}] Failed to open file in editor: {str(e)}")
            return False

    def open_in_vscode(self) -> bool:
        """Open the input file in VSCode"""
        if self.input_file_path is None:
            print(f"[{self.name}] No input file path configured")
            return False
        try:
            import subprocess

            subprocess.run(["code", self.input_file_path], check=False)
            print(f"[{self.name}] Opened input file in VSCode")
            return True
        except Exception as e:
            print(f"[{self.name}] Failed to open file in editor: {str(e)}")
            return False

    def open_in_jetbrains(self) -> bool:
        """Open the input file in JetBrains IDEs"""
        if self.input_file_path is None:
            print(f"[{self.name}] No input file path configured")
            return False

        try:
            import subprocess

            subprocess.run(["idea", self.input_file_path], check=False)
            print(f"[{self.name}] Opened input file in JetBrains IDE")
            return True
        except Exception as e:
            print(f"[{self.name}] Failed to open file in editor: {str(e)}")
            return False

    def run_input_file(self, skip_draft: bool = False) -> None:
        """Run the input file

        Args:
            skip_draft: Whether to skip draft files, default True
        """
        if self.input_file_path is None:
            print(f"[{self.name}] [red]No input file path configured[/red]")
            return

        if not os.path.exists(self.input_file_path):
            print(
                f"[{self.name}] [red][bold]Input file does not exist:[/bold] {self.input_file_path}[/red]"
            )
            return

        # load the input file (yaml)
        with open(self.input_file_path, "r") as f:
            input_file_data = yaml.safe_load(f)

        is_draft = input_file_data.get("draft", False)
        if is_draft and skip_draft:
            print(
                f"[{self.name}] [yellow][bold]Skipping draft:[/bold] {self.input_file_path}[/yellow]"
            )
            return
        # get cmd from input_file
        cmd = input_file_data.get("cmd")
        if not cmd:
            print(
                f"[{self.name}] [red][bold]No command found in input file[/bold][/red]"
            )
            return

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
            print(
                f"[{self.name}] [red][bold]Command not found:[/bold] {cmd_fn_name}[/red]"
            )
            return
        # full query
        full_query = cmd_extras + " " + input_file_data.get("content", "")
        # run the wrapped function
        # print panel with title "Running command" and full_query

        panel = Panel(
            f"Running command: [cyan]{full_query}[/cyan]",
            title="Running command",
            title_align="center",
        )
        print(panel)
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

    def prepare_event_file(self, cmd: str) -> None:
        """Prepare the event file for the given command"""
        if cmd in self.with_event_commands:
            self.create_event_file()

    def create_event_file(self) -> None:
        """Create the event file"""
        event_file, file_id = gengerate_event_file_path()
        configure(f"event_file:{event_file}")

    def shutdown(self) -> None:
        """Shutdown the plugin"""
        print(f"[{self.name}] Shutting down input file plugin")
