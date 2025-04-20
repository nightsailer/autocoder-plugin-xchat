"""
CodeBook plugin for managing code book functionality
"""

from typing import Any, Dict, Optional, Tuple, Callable, List
from rich import print
from rich.panel import Panel

from autocoder.plugins import Plugin, PluginManager
from autocoder_plugin_xchat.xchat.xchat import XChatApp


class XChatPlugin(Plugin):
    """xChat Plugin interface for AutoCoder"""

    name = "xChat"
    description = ""
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
        """Initialize plugin"""
        super().__init__(manager, config, config_path)

    def initialize(self) -> bool:
        """Initialize the plugin"""
        print(f"[{self.name}] Initializing xChat plugin")
        project_root = self.manager.project_root()
        if not project_root:
            print(f"[{self.name}] No project root found")
            return False
        return True

    def get_commands(self) -> Dict[str, Tuple[Callable, str]]:
        """Get commands provided by this plugin"""
        return {
            "xchat": (
                self.start_xchat,
                "Start xChat terminal",
            ),
        }

    def get_completions(self) -> Dict[str, List[str]]:
        """Get completions provided by this plugin"""
        return {
            "/xchat": [],
        }

    def start_xchat(self, args: str) -> None:
        """Start xtools"""
        print(f"[{self.name}] Starting xtools")
        app = XChatApp()
        app.run()

    def shutdown(self) -> None:
        """Shutdown the plugin"""
        print(f"[{self.name}] Shutting down input file plugin")
