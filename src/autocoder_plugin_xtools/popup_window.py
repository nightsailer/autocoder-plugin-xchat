from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import (
    Header,
    Footer,
    Static,
    Input,
    Button,
    Label,
    ListItem,
    ListView,
)
from textual.widget import Widget
from textual.reactive import var


# --- Custom Widget for List Items ---
# Represents a single item in the "Suggested" list
class SuggestedItem(Widget):
    DEFAULT_CSS = """
    SuggestedItem {
        layout: horizontal;
        height: 1;
        width: 100%;
        padding: 0 1; /* Padding left/right */
        align-vertical: middle; /* Vertically center content */
    }
    SuggestedItem > Static { /* Style child Statics directly */
        border: none;
        height: 1;
        content-align-vertical: middle; /* Ensure text is centered vertically */
    }
    SuggestedItem > .icon {
        width: 3;
        content-align: center middle; /* Center icon */
        color: $accent-lighten-1;
    }
    SuggestedItem > .title {
        width: 1fr; /* Take up remaining space */
        padding-left: 1;
    }
    SuggestedItem > .shortcut {
        width: auto; /* Size based on content */
        color: $text-muted; /* Dimmer color for shortcut */
        padding-left: 1;
        align: right middle; /* Align to the right */
    }

    /* Styling when the ListItem containing this widget is highlighted */
    ListItem.--highlight SuggestedItem > .icon {
         color: $text;
    }
    ListItem.--highlight SuggestedItem > .title {
         color: $text; /* Ensure text is readable on highlight */
    }
     ListItem.--highlight SuggestedItem > .shortcut {
         color: $text;
    }
    """

    def __init__(self, icon: str, title: str, shortcut: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.item_icon = icon
        self.item_title = title
        self.item_shortcut = shortcut

    def compose(self) -> ComposeResult:
        yield Static(self.item_icon, classes="icon")
        yield Static(self.item_title, classes="title")
        if self.item_shortcut:
            yield Static(self.item_shortcut, classes="shortcut")


# --- The Main PopupWindow Widget ---
class PopupWindow(Container):
    DEFAULT_CSS = """
    PopupWindow {
        /* Positioning & Sizing */
        /* To make it appear like a popup, center it and give fixed size */
        /* Option 1: Using grid on the parent screen */
        /* align: center middle; */ /* Center content within the popup */
        /* Option 2: Absolute positioning (more popup-like) - Requires parent with relative/absolute */
        layer: popup; /* Render on a higher layer */
        offset: 2 5;  /* Example offset from top-left */
        width: 80;   /* Fixed width */
        height: 25;  /* Fixed height */


        /* Appearance */
        background: $surface; /* Dark background */
        border: round $accent; /* Rounded border with accent color */
        padding: 1; /* Inner spacing */
        /* Using grid for internal layout */
        grid-size: 1; /* Single column grid */
        grid-gutter: 0 1;
    }

    /* Input field styling */
    PopupWindow > Input {
        margin-bottom: 1;
        border: tall $accent-darken-1;
        background: $panel-darken-1; /* Slightly different background */
    }

    /* Container for category buttons */
    #categories-container {
        height: auto; /* Auto height based on content */
        grid-size: 4; /* 4 columns for buttons */
        grid-gutter: 1 1; /* Spacing between buttons */
        margin-bottom: 1;
    }

    #categories-container > Button {
        width: 100%; /* Make buttons fill grid cells */
        background: $panel-lighten-1; /* Lighter button background */
        border: none;
        /* Optional: add round borders to buttons */
        /* border: round $primary-background; */
    }
    #categories-container > Button:hover {
        background: $panel-lighten-2; /* Slightly lighter on hover */
    }


    /* "Suggested" label styling */
    #suggested-label {
        margin-top: 1;
        margin-bottom: 1;
        text-style: bold;
    }

    /* ListView styling */
    PopupWindow > ListView {
        background: $surface; /* Match popup background */
        border: none; /* Remove default ListView border */
    }

     /* Highlight style for ListView items */
    ListView > ListItem.--highlight {
        background: $accent; /* Use accent color for highlight */
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search for a command")
        # Container for the category buttons using a grid
        with Container(id="categories-container"):
            yield Button(
                "workflows"
            )  # Add icons/symbols if desired: Button(" workflows") etc.
            yield Button("prompts")
            yield Button("notebooks")
            yield Button("env vars")
            yield Button("Warp Drive")
            yield Button("actions")
            yield Button("sessions")
            yield Button("launch cfgs")
        yield Label("Suggested", id="suggested-label")
        # Use ListView for the suggested items
        with ListView(id="suggestions-list"):
            # Wrap our custom SuggestedItem widget in a standard ListItem
            yield ListItem(SuggestedItem("✨", "Toggle Agent Mode", "⌘ |"))
            yield ListItem(
                SuggestedItem("💲", "Create New Personal Workflow")
            )  # No shortcut
            yield ListItem(SuggestedItem("🎨", "Open Theme Picker", "⇧ ⌘ T"))
            yield ListItem(SuggestedItem("⚙️", "Settings"))
            yield ListItem(SuggestedItem("❓", "Help / Documentation"))


# --- Example App to Display the Popup ---
class PopupApp(App):
    BINDINGS = [("escape", "quit", "Quit")]
    CSS = """
    Screen {
        /* Center the popup using grid layout on the screen */
        align: center middle;
        /* Add some background pattern for contrast if desired */
        /* background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQIW2NkYGD4D8QgwAhjFBCMAAsQgwAA7pQG8ISJP5YAAAAASUVORK5CYII=) repeat; */

    }
    """

    def compose(self) -> ComposeResult:
        # yield Header() # Optional Header
        yield PopupWindow()  # Add our popup widget directly to the screen
        # yield Footer() # Optional Footer

    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = PopupApp()
    app.run()
