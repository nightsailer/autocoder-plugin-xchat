from textual.app import App, ComposeResult
from textual.widgets import (
    Static,
    Input,
    Footer,
    Button,
    RichLog,
    Label,
)
from textual.containers import Container, Horizontal, Vertical, Center
from textual.reactive import var
from typing import List, Tuple, ClassVar
from enum import Enum


class RunMode(Enum):
    """Run mode for XChat application"""

    PLUGIN = "plugin_mode"
    STANDALONE = "standalone_mode"


class XChatApp(App):
    BINDINGS = [
        ("q", "quit", "退出xChat"),
    ]
    CSS_PATH = ["xchat.tcss"]
    TITLE = "xChat"

    def __init__(self, run_mode: RunMode = RunMode.PLUGIN):
        super().__init__()
        # 使用内置的 dracula 主题
        self.theme = "dracula"
        self.run_mode = run_mode

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Container(classes="header"):
            yield Label(f"xChat  🚀 AutoCoder", classes="title")
        # button groups, action bar
        action_bar = Container(id="action-bar", classes="")
        action_bar.border_title = "Codebook"
        action_bar.border_subtitle = "<codebook / 未加载>"
        with action_bar:
            with Horizontal(id="action-bar-buttons"):
                yield Button(
                    "[purple]e[/] 加载",
                    id="new-book-button",
                    variant="primary",
                )
                yield Button(
                    "[purple]r[/] 运行",
                    id="run-button",
                    variant="primary",
                )
                yield Button(
                    "[purple]c[/] 停止",
                    id="stop-button",
                    variant="primary",
                )
            with Container(id="book-name-container", classes="center"):
                yield Static(
                    "<empty codebook>",
                    id="book-name",
                    classes="",
                )
        main_log = Container(id="main-log", classes="")
        main_log.border_title = "终端"
        with main_log:
            yield RichLog(id="log-content")
        yield Footer(show_command_palette=False)


if __name__ == "__main__":
    app = XChatApp()
    app.run()
