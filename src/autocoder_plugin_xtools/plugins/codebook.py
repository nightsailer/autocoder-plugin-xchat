"""
CodeBook plugin for managing code book functionality
"""

from typing import Any, Dict, Optional, Tuple, Callable, List
import yaml
from rich import print
from rich.panel import Panel

from autocoder.plugins import Plugin, PluginManager
from autocoder.auto_coder_runner import (
    configure,
    mcp,
    manage_models,
    gen_and_exec_shell_command,
)
from autocoder.events.event_manager_singleton import gengerate_event_file_path
from autocoder_plugin_xtools.xchat import XTools


class XtoolsPlugin(Plugin):
    """Plugin for Xtools"""

    name = "xtools"
    description = "Plugin for Xtools"
    version = "0.1.0"
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
        return True

    def get_commands(self) -> Dict[str, Tuple[Callable, str]]:
        """Get commands provided by this plugin"""
        return {
            "xtools": (
                self.start_xtools,
                "Start xtools",
            ),
        }

    def get_completions(self) -> Dict[str, List[str]]:
        """Get completions provided by this plugin"""
        return {
            "/xtools": [],
        }

    def start_xtools(self, args: str) -> None:
        """Start xtools"""
        print(f"[{self.name}] Starting xtools")
        app = XTools()
        app.run()

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
