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
from typing import List, Tuple


class XTools(App):
    # Add key binding for ctrl+d to quit
    BINDINGS: List[Tuple[str, str, str]] = [
        ("q", "quit", "退出XTools"),
    ]
    CSS_PATH = ["xchat.tcss"]
    TITLE = "XTools"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Container(classes="header"):
            yield Label(f"XTools [blue] 🚀 AutoCoder[/blue]", classes="title")
        # button groups, action bar
        with Container(id="action-bar", classes=""):
            with Horizontal(id="action-bar-buttons"):
                yield Button("新建|打开", id="new-book-button")
                yield Button(
                    "运行",
                    id="run-button",
                )
            with Container(id="book-name-container", classes="center"):
                yield Static("Book Name", id="book-name", classes="")
        with Container(id="main-log", classes=""):
            yield RichLog(id="log-content")
        yield Footer()


if __name__ == "__main__":
    app = XTools()
    app.run()
