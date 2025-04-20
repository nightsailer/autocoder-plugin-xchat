"""
Main entry point for the input file plugin
"""

import os
import sys
from autocoder.plugins import register_global_plugin_dir


def install_plugin():
    """Install the xChat plugin and register it globally."""
    # Get the current directory (where your plugin code is located)
    plugin_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        # Register the plugin directory globally
        register_global_plugin_dir(plugin_dir)
        print(f"✅ Successfully registered xChat plugin directory: {plugin_dir}")
        print(f"The xChat plugins are now available in all Chat Auto Coder projects.")
        return True
    except Exception as e:
        print(f"❌ Error during xChat plugin installation: {str(e)}")
        return False


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        if install_plugin():
            print("xChat installation completed successfully!")
        return


if __name__ == "__main__":
    main()
