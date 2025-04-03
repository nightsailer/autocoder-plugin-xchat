from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Footer, Header
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import var
from typing import List, Tuple


class CommandRow(Static):
    """一个显示命令及其快捷键的自定义小部件。"""

    def __init__(self, command_name: str, keys: list[str]) -> None:
        super().__init__()
        self.command_name = command_name
        self.keys = keys

    def compose(self) -> ComposeResult:
        """创建子小部件。"""
        with Horizontal(classes="command-row"):
            yield Static(self.command_name, classes="label")
            with Container(classes="keys-container"):
                for key in self.keys:
                    yield Static(key, classes="key")


class XChat(App):
    # Add key binding for ctrl+d to quit
    BINDINGS: List[Tuple[str, str, str]] = []
    CSS_PATH = ["xchat.tcss"]

    status_prefix = var("xtools git : ( feature / ui - main ) ± 1 A Pair * ")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Container(id="main-content"):
            with Vertical(id="commands-list"):
                yield CommandRow("Command Palette", ["⌘", "P"])
                yield CommandRow("Command Search", ["⇧", "R"])
                yield CommandRow("Agent Mode", ["⌘", "I"])

        with Container(id="status-bar"):
            with Horizontal(id="prompt-bar"):
                yield Static(self.status_prefix, id="status-prefix", shrink=True)
            yield Input(
                placeholder="输入消息...",
                id="command-input",
            )


if __name__ == "__main__":
    app = XChat()
    app.run()
