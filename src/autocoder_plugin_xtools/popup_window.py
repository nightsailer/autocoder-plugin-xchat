# 导入必要的 Textual 组件
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container  # 导入 Container
from textual.widgets import Header, Footer, Static, Input, Button, Label
from textual.widget import Widget
from textual.reactive import reactive
from textual.binding import Binding
from typing import Any  # 导入 Any 用于类型提示


# --- 可复用的建议项组件 ---
class SuggestedItem(Widget):
    """显示建议命令的自定义小部件"""

    DEFAULT_CSS = """
    SuggestedItem {
        layout: horizontal;
        height: auto; /* 保持 auto 以适应内容 */
        width: 100%; /* 确保宽度充满父容器 */
        margin-bottom: 1;
        padding: 0 1; /* 左右内边距 */
    }
    SuggestedItem:hover {
        /* 尝试更明显的悬停背景色 */
        background: #4f5261;
    }
    SuggestedItem .icon {
        width: 3;
        content-align: center middle;
        color: #f1fa8c;
    }
    SuggestedItem .text {
        width: 1fr;
        padding-left: 1;
    }
    SuggestedItem .shortcut {
        width: auto;
        color: #6272a4;
        padding-left: 1;
    }
    /* 图标颜色类 */
    .icon-toggle { color: #f1fa8c; }
    .icon-create { color: #50fa7b; }
    .icon-theme { color: #bd93f9; }
    """
    icon = reactive(" ")
    text = reactive(" ")
    shortcut = reactive(" ")

    def __init__(self, icon: str, text: str, shortcut: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.icon = icon
        self.text = text
        self.shortcut = shortcut

    def compose(self) -> ComposeResult:
        yield Label(self.icon, classes="icon")
        yield Label(self.text, classes="text")
        yield Label(self.shortcut, classes="shortcut")


# --- 可复用的命令搜索组件 ---
class CommandSearchWidget(Container):  # 继承自 Container
    """一个封装了命令搜索界面的可复用组件"""

    DEFAULT_CSS = """
    CommandSearchWidget {
        width: 80;
        height: auto; /* 高度自适应内容 */
        max-height: 25; /* 增加最大高度以容纳更多内容 */
        background: #282a36;
        border: round #44475a;
        padding: 1;
        /* 使用垂直布局来管理内部元素 */
        layout: vertical;
    }
    CommandSearchWidget > Input {
        border: tall #6272a4;
        margin-bottom: 1;
        background: #44475a;
        height: 3; /* 固定输入框高度 */
        /* flex-shrink: 0;  <-- 移除无效属性 */
    }
    CommandSearchWidget > Input:focus {
        border: tall #bd93f9;
    }
    CommandSearchWidget #button-row-1, CommandSearchWidget #button-row-2 {
        height: auto; /* 按钮行高度自适应 */
        margin-bottom: 1;
        /* flex-shrink: 0;  <-- 移除无效属性 */
    }
    CommandSearchWidget Button {
        border: round #6272a4;
        background: #44475a;
        color: #f8f8f2;
        margin: 0 1;
        min-width: 8;
        height: 3;
        content-align: center middle;
    }
    CommandSearchWidget Button:hover {
        background: #6272a4;
        border: round #bd93f9;
    }
    CommandSearchWidget #suggested-label {
        color: #8be9fd;
        margin-top: 1; /* 调整与按钮行的间距 */
        height: 1; /* 固定标签高度 */
        /* flex-shrink: 0;  <-- 移除无效属性 */
    }
    /* 为建议列表容器添加样式 */
    CommandSearchWidget #suggestions-list-container {
         /* 让此容器占据剩余的垂直空间 */
        height: 1fr;
        width: 100%;
        /* 启用垂直滚动 */
        overflow-y: scroll;
        /* 可以添加背景色以区分 */
        /* background: #2f313d; */
    }

    /* 按钮图标颜色类 */
    .icon-workflow { color: #ff79c6; }
    .icon-prompt { color: #ffb86c; }
    .icon-notebook { color: #8be9fd; }
    .icon-env { color: #ff5555; }
    .icon-drive { color: #50fa7b; }
    .icon-actions { color: #bd93f9; }
    .icon-sessions { color: #f1fa8c; }
    .icon-launch { color: #ffb86c; }
    """

    def compose(self) -> ComposeResult:
        """创建组件的 UI 布局"""
        yield Input(placeholder="Search for a command")
        with Horizontal(id="button-row-1"):
            yield Button(
                " workflows",
                variant="default",
                id="btn-workflows",
                classes="icon-workflow",
            )
            yield Button(
                " prompts", variant="default", id="btn-prompts", classes="icon-prompt"
            )
            yield Button(
                " notebooks",
                variant="default",
                id="btn-notebooks",
                classes="icon-notebook",
            )
            yield Button(
                " env vars", variant="default", id="btn-env", classes="icon-env"
            )
        with Horizontal(id="button-row-2"):
            yield Button(
                " Warp Drive", variant="default", id="btn-drive", classes="icon-drive"
            )
            yield Button(
                " actions", variant="default", id="btn-actions", classes="icon-actions"
            )
            yield Button(
                " sessions",
                variant="default",
                id="btn-sessions",
                classes="icon-sessions",
            )
            yield Button(
                " launch", variant="default", id="btn-launch", classes="icon-launch"
            )

        yield Static("Suggested", id="suggested-label")

        # 将 Vertical(id="suggestions-list") 放入一个容器以便应用滚动
        with Container(id="suggestions-list-container"):
            with Vertical(id="suggestions-list"):  # 保持这个 Vertical 用于排列项目
                # 添加更多项目以测试滚动
                yield SuggestedItem(
                    "⚡",
                    "Toggle Agent Mode",
                    "⌘ K",
                    id="suggest-toggle",
                    classes="icon-toggle",
                )
                yield SuggestedItem(
                    "✨",
                    "Create a New Personal Workflow",
                    "",
                    id="suggest-create",
                    classes="icon-create",
                )
                yield SuggestedItem(
                    "⚙️",
                    "Open Theme Picker",
                    "⇧ ⌘ T",
                    id="suggest-theme",
                    classes="icon-theme",
                )
                yield SuggestedItem(
                    "🔧", "Another Action Item", "Alt+A", id="suggest-action"
                )
                yield SuggestedItem("💡", "Show Help", "?", id="suggest-help")
                yield SuggestedItem(
                    "🚀", "Launch Something Else", "Ctrl+L", id="suggest-launch-else"
                )


# --- 主应用程序 (使用新组件) ---
class CommandSearchApp(App):
    """使用 CommandSearchWidget 组件的 Textual 应用"""

    CSS = """
    Screen {
        background: #1e1e2e;
        align: center middle;
    }
    """
    BINDINGS = [Binding("ctrl+c", "quit", "Quit", show=False, priority=True)]

    def compose(self) -> ComposeResult:
        """创建应用程序 UI，只包含可复用组件"""
        yield CommandSearchWidget()


if __name__ == "__main__":
    app = CommandSearchApp()
    app.run()
