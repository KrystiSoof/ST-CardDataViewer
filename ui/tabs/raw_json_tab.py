"""Raw JSON tab implementation."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, Any, Optional
import logging

from core.formatter import format_json, validate_json

logger = logging.getLogger('SillyTavernCardEditor')


class RawJsonTab:
    """Handles the Raw JSON tab UI and data management."""

    def __init__(self, parent: ttk.Notebook):
        """
        Initialize the Raw JSON tab.

        Args:
            parent: Parent notebook widget
        """
        self.tab = ttk.Frame(parent, padding="10")
        parent.add(self.tab, text="🔧 Raw JSON")

        self.data_text: scrolledtext.ScrolledText = None  # type: ignore[assignment]

        self.create_widgets()
        logger.debug("Raw JSON tab initialized")

    def create_widgets(self) -> None:
        """Create all widgets for the Raw JSON tab."""
        self.data_text = scrolledtext.ScrolledText(
            self.tab,
            wrap=tk.WORD,
            font=("Consolas", 10),
            width=70,
            height=30
        )
        self.data_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore[arg-type]

        self.tab.columnconfigure(0, weight=1)
        self.tab.rowconfigure(0, weight=1)

    def populate(self, data: Dict[str, Any]) -> None:
        """
        Populate JSON text from character data.

        Args:
            data: Character data dictionary
        """
        import json

        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(1.0, json_str)

        logger.debug("Raw JSON tab populated")

    def get_data(self) -> Optional[Dict[str, Any]]:
        """
        Get parsed data from JSON text.

        Returns:
            Parsed data dictionary or None if invalid
        """
        json_text = self.data_text.get(1.0, tk.END).strip()

        if not json_text or json_text.startswith('#'):
            return None

        is_valid, error, data = validate_json(json_text)

        if not is_valid:
            logger.error(f"Invalid JSON: {error}")
            return None

        return data

    def clear(self) -> None:
        """Clear JSON text."""
        self.data_text.delete(1.0, tk.END)
        logger.debug("Raw JSON tab cleared")

    def format(self) -> bool:
        """
        Format the JSON data.

        Returns:
            True if successful, False otherwise
        """
        json_text = self.data_text.get(1.0, tk.END).strip()

        if not json_text:
            return False

        formatted = format_json(json_text)

        if formatted is None:
            messagebox.showerror(
                "Error",
                "Invalid JSON format.\nPlease fix the JSON before formatting."
            )
            return False

        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(1.0, formatted)
        return True

    def search(self, search_term: str, replace_with: Optional[str] = None) -> int:
        """
        Search or search-and-replace in the JSON text.

        Args:
            search_term: Text to search for
            replace_with: Optional replacement text

        Returns:
            Number of matches found
        """
        if not search_term:
            return 0

        content = self.data_text.get(1.0, tk.END)

        if replace_with is not None:
            # Replace all occurrences
            count = content.count(search_term)
            new_content = content.replace(search_term, replace_with)

            self.data_text.delete(1.0, tk.END)
            self.data_text.insert(1.0, new_content)

            logger.info(f"Replaced {count} occurrences of '{search_term}' with '{replace_with}'")
            return count
        else:
            # Just count matches
            count = content.count(search_term)
            logger.info(f"Found {count} occurrences of '{search_term}'")
            return count
