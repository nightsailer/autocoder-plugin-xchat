"""
CodeBook plugin for managing code book functionality
"""

import os
from typing import Any, Dict, Optional, Tuple, Callable, List
import yaml
from rich import print
from rich.panel import Panel
from williamtoolbox.server.apps.annotation_router import executor

from autocoder.plugins import Plugin, PluginManager
from autocoder_plugin_xtools.codebook import (
    CodebookParser,
    CodebookWatcher,
    CodebookEditor,
    CodebookExecutor,
)
from autocoder.auto_coder_runner import (
    configure,
    mcp,
    manage_models,
    gen_and_exec_shell_command,
)
from autocoder.events.event_manager_singleton import gengerate_event_file_path


class CodeBookPlugin(Plugin):
    """Plugin for managing code book functionality"""

    name = "xtools_codebook"
    description = "Plugin for managing code book functionality"
    version = "0.1.0"
    input_file_path = None
    input_file_name = "codebook.yaml"
    book_tpl_path = os.path.join(os.path.dirname(__file__), "codebook_tpl.yaml")
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
        self.supported_commands = self.manager.get_wrapped_functions()
        self.supported_commands.update(
            {
                "conf": configure,
                "auto": self.supported_commands["auto_command"],  # alias
                "mcp": mcp,
                "models": manage_models,
                "add_models_by_provider": self.add_models_by_provider,
            }
        )
        return True

    def get_commands(self) -> Dict[str, Tuple[Callable, str]]:
        """Get commands provided by this plugin"""
        return {
            "xtools/codebook/watch": (
                self.watch_codebook,
                "Start watching the codebook",
            ),
            "xtools/codebook/run": (self.run_codebook, "Run the codebook"),
        }

    def get_completions(self) -> Dict[str, List[str]]:
        """Get completions provided by this plugin"""
        return {
            "/xtools/codebook/watch": [],
            "/xtools/codebook/run": [],
        }

    def watch_codebook(self, args: str = "") -> None:
        """Watch the codebook

        Args:
            args: Command arguments (unused)
        """
        print(f"[{self.name}] Starting codebook watching")

        if self.input_file_path is None:
            print(f"[{self.name}] No codebook path configured")
            return

        if not os.path.exists(self.input_file_path):
            self.create_codebook()

        if not os.path.exists(self.input_file_path):
            print(
                f"[{self.name}] Codebook creation failed: [red]{self.input_file_path}[/red]"
            )
            return

        # Open in editor
        editor = CodebookEditor(self.input_file_path)
        if not editor.open():
            print(
                f"[{self.name}] Please open [bold yellow]{self.input_file_path}[/bold yellow] to edit"
            )

        # Start watching
        watcher = CodebookWatcher(
            self.input_file_path, lambda: self.run_codebook(skip_draft=True)
        )
        watcher.start()

    def run_codebook(
            self, skip_draft: bool = False, codebook_path: Optional[str] = None
    ) -> None:
        """Run the codebook

        Args:
            skip_draft: Whether to skip draft files, default True
            codebook_path: Optional path to codebook file
        """
        if codebook_path is None:
            codebook_path = self.input_file_path
        if codebook_path is None:
            print(f"[{self.name}] [red]No codebook path configured[/red]")
            return

        # Parse codebook
        parser = CodebookParser(codebook_path)
        success, data, error = parser.parse()
        if not success:
            print(f"[{self.name}] [red]{error}[/red]")
            return

        # Check if draft
        if parser.is_draft(data) and skip_draft:
            print(
                f"[{self.name}] [yellow][bold]Skipping draft:[/bold] {codebook_path}[/yellow]"
            )
            return

        # Get command
        success, cmd, error = parser.get_command(data)
        if not success:
            print(f"[{self.name}] [red]{error}[/red]")
            return

        # Get content
        content = parser.get_content(data)

        # Run command
        executor = CodebookExecutor(self.supported_commands)
        executor.run(cmd, content)

    def create_codebook(self, codebook_path: Optional[str] = None) -> None:
        """Create the codebook with template content"""
        if codebook_path is None:
            codebook_path = self.input_file_path
        if codebook_path is None:
            return

        if os.path.exists(codebook_path):
            print(f"[{self.name}] Codebook already exists: {codebook_path}")
            return

        # Get template file path
        template_path = self.book_tpl_path
        if not os.path.exists(template_path):
            print(f"[{self.name}] Template file not found: {template_path}")
            return

        # Create directory if not exists
        os.makedirs(os.path.dirname(codebook_path), exist_ok=True)

        # Copy template content to input file
        with open(template_path, "r") as template_file:
            template_content = template_file.read()

        with open(codebook_path, "w") as f:
            f.write(template_content)

        print(f"[{self.name}] Created codebook at {codebook_path} using template")

    def prepare_event_file(self, cmd: str) -> None:
        """Prepare the event file for the given command"""
        if cmd in self.with_event_commands:
            self.create_event_file()

    def create_event_file(self) -> None:
        """Create the event file"""
        event_file, file_id = gengerate_event_file_path()
        configure(f"event_file:{event_file}")

    def add_models_by_provider(self, args: str) -> None:
        """Add models by provider"""
        # yaml from args
        yaml_data = yaml.safe_load(args)
        provider_name = yaml_data.get("provider_name")
        api_key = yaml_data.get("access_key")
        api_endpoint_url = yaml_data.get("api_endpoint_url")
        models = yaml_data.get("models")
        if not provider_name:
            print(
                f"[{self.name}] [red][bold]Missing provider name:[/bold] {args}[/red]"
            )
            return
        if not api_key or api_key == "<INPUT_YOUR_KEY>":
            print(f"[{self.name}] [red][bold]Missing API key:[/bold] {args}[/red]")
            return
        if not api_endpoint_url:
            print(
                f"[{self.name}] [red][bold]Missing API endpoint URL:[/bold] {args}[/red]"
            )
            return
        if not models:
            print(f"[{self.name}] [red][bold]Missing models:[/bold] {args}[/red]")
            return
        # print panel with title "Adding models by provider" and provider_name
        panel = Panel(
            f"Adding models by provider: [cyan]{provider_name}[/cyan]",
            title="Adding models by provider",
            title_align="center",
        )
        print(panel)
        # add models
        for model in models:
            print(f"[{self.name}] Adding model: {model}")
            model_id = f"{provider_name}_{model['name']}"
            add_model_query = f"/add_model name={model_id} model_name={model['model']} api_key={api_key} base_url={api_endpoint_url}"
            add_query = f"/add {model_id} {api_key}"
            try:
                manage_models(add_model_query)
                manage_models(add_query)
                print(
                    f"[{self.name}] [green][bold]Added model:[/bold] {model_id}[/green]"
                )
            except Exception as e:
                print(f"[{self.name}] [red][bold]Failed to add model:[/bold] {e}[/red]")

    def shutdown(self) -> None:
        """Shutdown the plugin"""
        print(f"[{self.name}] Shutting down input file plugin")
