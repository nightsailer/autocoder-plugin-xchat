from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Footer, Header
from textual.containers import Container
from typing import List, Tuple


class XChat(App):
    # Add key binding for ctrl+d to quit
    BINDINGS: List[Tuple[str, str, str]] = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(id="main-content")
        yield Input(
            placeholder="输入消息...",
            id="input-box",
        )
        # yield Footer()

    def on_mount(self) -> None:
        """Set up the layout when the app starts."""
        # self.query_one("#main-content").styles.height = "1fr"
        # self.query_one("#main-content").styles.overflow_y = "auto"
        # self.query_one("#input-box").styles.dock = "bottom"
        # self.query_one("#input-box").styles.padding = (1, 2)
        # self.query_one("#input-box").styles.background = "blue"


if __name__ == "__main__":
    app = XChat()
    app.run()
