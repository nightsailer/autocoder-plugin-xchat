"""
CodeBook editor module for handling editor integration
"""

import os
import subprocess
from typing import Optional
from autocoder_plugin_xtools.plugins.utils import (
    is_cursor_environment,
    is_vscode_environment,
    is_jetbrains_environment,
)

book_tpl_path = os.path.join(os.path.dirname(__file__), "codebook.yaml")


class CodebookEditor:
    """Editor integration for codebook files"""

    def __init__(self, file_path: str):
        """Initialize the editor

        Args:
            file_path: Path to the codebook file
        """
        self.file_path = file_path

    def open(self) -> bool:
        """Open the codebook file in the appropriate editor

        Returns:
            bool: True if file was opened successfully
        """
        if not self.file_path:
            print("No codebook path configured")
            return False

        if is_cursor_environment():
            return self._open_in_cursor()
        elif is_vscode_environment():
            return self._open_in_vscode()
        elif is_jetbrains_environment():
            return self._open_in_jetbrains()
        else:
            print(f"Please open [bold yellow]{self.file_path}[/bold yellow] to edit")
            return False

    def create_codebook(self, codebook_path: Optional[str] = None) -> None:
        """Create the codebook with template content"""
        if codebook_path is None:
            codebook_path = self.file_path
        if codebook_path is None:
            return

        if os.path.exists(codebook_path):
            print(f"Codebook already exists: {codebook_path}")
            return

        # Get template file path
        template_path = self.book_tpl_path
        if not os.path.exists(template_path):
            print(f"[{self.name}] Template file not found: {template_path}")
            return

        # Create directory if not exists
        os.makedirs(os.path.dirname(codebook_path), exist_ok=True)

        # Copy template content to input file
        with open(template_path, "r") as template_file:
            template_content = template_file.read()

        with open(codebook_path, "w") as f:
            f.write(template_content)

        print(f"[{self.name}] Created codebook at {codebook_path} using template")

    def _open_in_cursor(self) -> bool:
        """Open file in Cursor editor"""
        try:
            subprocess.run(["cursor", self.file_path], check=False)
            print("Opened file in Cursor")
            return True
        except Exception as e:
            print(f"Failed to open file in Cursor: {str(e)}")
            return False

    def _open_in_vscode(self) -> bool:
        """Open file in VSCode editor"""
        try:
            subprocess.run(["code", self.file_path], check=False)
            print("Opened file in VSCode")
            return True
        except Exception as e:
            print(f"Failed to open file in VSCode: {str(e)}")
            return False

    def _open_in_jetbrains(self) -> bool:
        """Open file in JetBrains IDE"""
        try:
            subprocess.run(["idea", self.file_path], check=False)
            print("Opened file in JetBrains IDE")
            return True
        except Exception as e:
            print(f"Failed to open file in JetBrains IDE: {str(e)}")
            return False
