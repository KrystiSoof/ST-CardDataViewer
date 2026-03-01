"""
SillyTavern Character Card Data Viewer and Editor
Entry point for the application.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import tkinter as tk
from ui.main_window import SillyTavernCardEditor
from utils.logger import setup_logger

# Setup logging
logger = setup_logger()


def main():
    """Main entry point for the application."""
    try:
        root = tk.Tk()
        _app = SillyTavernCardEditor(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

