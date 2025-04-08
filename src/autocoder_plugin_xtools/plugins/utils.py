import os


def is_cursor_environment() -> bool:
    """Check if running in Cursor environment"""
    return "CURSOR_TRACE_ID" in os.environ


def is_vscode_environment() -> bool:
    """Check if running in VSCode environment"""
    return "TERM_PROGRAM" in os.environ and "vscode" in os.environ["TERM_PROGRAM"]


def is_jetbrains_environment() -> bool:
    """Check if running in JetBrains environment"""
    terminal_emulator = os.getenv("TERMINAL_EMULATOR")
    if terminal_emulator:
        return "JetBrains" in terminal_emulator
    return False
