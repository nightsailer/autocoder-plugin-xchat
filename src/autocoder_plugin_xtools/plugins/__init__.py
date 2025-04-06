"""
Input file plugin module for autocoder
"""

import os
import sys
from pathlib import Path

from autocoder.plugins import register_global_plugin_dir
from .input_file import InputFilePlugin

__all__ = ["InputFilePlugin"]


def install_plugin():
    """Install the input file plugin and register it globally."""
    # Get the current directory (where your plugin code is located)
    plugin_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        # Register the plugin directory globally
        register_global_plugin_dir(plugin_dir)
        print(f"✅ Successfully registered input file plugin directory: {plugin_dir}")
        print(
            f"The input file plugin is now available in all Chat Auto Coder projects."
        )

        return True
    except Exception as e:
        print(f"❌ Error during input file plugin installation: {str(e)}")
        return False


if __name__ == "__main__":
    if install_plugin():
        print("Input file plugin installation completed successfully!")
    else:
        print(
            "Input file plugin installation failed. Please check the error messages above."
        )
