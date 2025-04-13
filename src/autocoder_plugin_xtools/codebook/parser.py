"""
CodeBook parser module for parsing codebook files
"""

import os
import yaml
from typing import Dict, Any, Optional, Tuple


class CodebookParser:
    """Parser for codebook files"""

    def __init__(self, file_path: str):
        """Initialize the parser with a file path"""
        self.file_path = file_path

    def parse(self) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Parse the codebook file

        Returns:
            Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
                (success, parsed_data, error_message)
        """
        if not os.path.exists(self.file_path):
            return False, None, f"Codebook does not exist: {self.file_path}"

        try:
            with open(self.file_path, "r") as f:
                data = yaml.safe_load(f)
            return True, data, None
        except Exception as e:
            return False, None, f"Failed to parse codebook: {str(e)}"

    def get_command(
        self, data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Extract command from parsed data

        Args:
            data: Parsed codebook data

        Returns:
            Tuple[bool, Optional[str], Optional[str]]:
                (success, command, error_message)
        """
        cmd = data.get("cmd")
        if not cmd:
            return False, None, "No command found in codebook"
        return True, cmd, None

    def get_content(self, data: Dict[str, Any]) -> str:
        """Extract content from parsed data

        Args:
            data: Parsed codebook data

        Returns:
            str: Content string
        """
        return data.get("content", "")

    def is_draft(self, data: Dict[str, Any]) -> bool:
        """Check if codebook is a draft

        Args:
            data: Parsed codebook data

        Returns:
            bool: True if codebook is a draft
        """
        return data.get("draft", False)
