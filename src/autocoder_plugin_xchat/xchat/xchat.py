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
from typing import List, Tuple, ClassVar, Optional
from enum import Enum
from autocoder_plugin_xchat.codebook.manager import CodebookManager
from autocoder_plugin_xchat.codebook.executor import CodebookExecutor
from autocoder_plugin_xchat.codebook.watcher import CodebookWatcher
import os


class RunMode(Enum):
    """Run mode for XChat application"""

    PLUGIN = "plugin_mode"
    STANDALONE = "standalone_mode"


class XChatApp(App):
    BINDINGS = [
        ("q", "quit", "退出xChat"),
        ("e", "new_book", "加载Codebook"),
        ("r", "run_code", "自动运行"),
        ("c", "stop_code", "停止运行"),
    ]
    CSS_PATH = ["xchat.tcss"]
    TITLE = "xChat"

    is_running: var[bool] = var(False)
    loaded: var[bool] = var(False)
    codebook_manager: Optional[CodebookManager] = None
    watch_worker = None

    def __init__(self, run_mode: RunMode = RunMode.PLUGIN):
        super().__init__()
        # 使用内置的 dracula 主题
        self.theme = "dracula"
        self.run_mode = run_mode
        # 避免在初始化时触发更新
        self.set_reactive(XChatApp.is_running, False)
        self.set_reactive(XChatApp.loaded, False)
        # 初始化Codebook管理器
        self.codebook_manager = CodebookManager(
            os.getcwd(), lambda msg: self._log_message(msg)
        )

    def _log_message(self, message: str) -> None:
        """Log a message to the RichLog

        Args:
            message: Message to log
        """
        self.query_one("#log-content", RichLog).write(message)

    def on_mount(self) -> None:
        """Called when the app is mounted"""
        self.update_button_states()

    def update_button_states(self) -> None:
        """Update all button states"""
        run_button = self.query_one("#run-button", Button)
        stop_button = self.query_one("#stop-button", Button)
        run_button.disabled = not self.loaded or self.is_running
        stop_button.disabled = not self.is_running

    def watch_loaded(self, loaded: bool) -> None:
        """Update button states when loaded state changes"""
        self.update_button_states()

    def watch_is_running(self, is_running: bool) -> None:
        """Update button states when running state changes"""
        self.update_button_states()

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
                    "[red]e[/] 加载",
                    id="new-book-button",
                    variant="primary",
                    action="action_new_book",
                )
                yield Button(
                    "[red]r[/] 运行",
                    id="run-button",
                    variant="primary",
                    action="action_run_code",
                )
                yield Button(
                    "[red]c[/] 停止",
                    id="stop-button",
                    variant="primary",
                    action="action_stop_code",
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
            yield RichLog(id="log-content", markup=True)
        yield Footer(show_command_palette=False)

    def action_new_book(self) -> None:
        """Handle new book button click"""
        self.query_one("#book-name", Static).update("正在加载代码本...")
        if self.codebook_manager and self.codebook_manager.load_codebook():
            self.loaded = True
            self._log_message("[green]代码本加载成功[/green]")
            self.query_one("#book-name", Static).update("代码本已加载")
        else:
            self._log_message("[red]代码本加载失败[/red]")
            self.query_one("#book-name", Static).update("加载失败")

    def action_run_code(self) -> None:
        """Handle run button click"""
        if self.is_running:
            self.notify("代码正在运行中", severity="warning")
            return
        if not self.loaded:
            self.notify("请先加载代码本", severity="warning")
            return

        self.is_running = True
        self._log_message("[yellow]开始监控代码本变更...[/yellow]")

        # 启动监控
        self.watch_worker = self.run_worker(
            self._watch_codebook, name="codebook-watcher"
        )

    def action_stop_code(self) -> None:
        """Handle stop button click"""
        if not self.is_running:
            self.notify("没有正在运行的代码", severity="warning")
            return

        if self.watch_worker:
            self.watch_worker.cancel()
            self.watch_worker = None

        self.is_running = False
        self._log_message("[yellow]停止监控代码本变更[/yellow]")

    async def _watch_codebook(self) -> None:
        """Worker function for watching codebook"""
        if self.codebook_manager:
            try:
                await self.codebook_manager.start_watching({})  # TODO: 添加命令注册表
            except Exception as e:
                self._log_message(f"[red]监控出错: {str(e)}[/red]")
                self.is_running = False
                self.watch_worker = None


if __name__ == "__main__":
    app = XChatApp()
    app.run()
