"""Messages tab implementation."""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any
import logging

logger = logging.getLogger('SillyTavernCardEditor')


class MessagesTab:
    """Handles the Messages tab UI and data management."""

    def __init__(self, parent: ttk.Notebook):
        """
        Initialize the Messages tab.

        Args:
            parent: Parent notebook widget
        """
        self.tab = ttk.Frame(parent, padding="10")
        parent.add(self.tab, text="💬 Messages")

        self.first_mes_text: scrolledtext.ScrolledText = None  # type: ignore[assignment]
        self.mes_example_text: scrolledtext.ScrolledText = None  # type: ignore[assignment]
        self.alt_greetings_text: scrolledtext.ScrolledText = None  # type: ignore[assignment]

        self.create_widgets()
        logger.debug("Messages tab initialized")

    def create_widgets(self) -> None:
        """Create all widgets for the Messages tab."""
        # First Message
        ttk.Label(self.tab, text="First Message (Greeting):", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.first_mes_text = scrolledtext.ScrolledText(
            self.tab, height=6, width=70, wrap=tk.WORD, font=("Arial", 10)
        )
        self.first_mes_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore[arg-type]

        # Example Messages
        ttk.Label(self.tab, text="Example Messages (mes_example):", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.mes_example_text = scrolledtext.ScrolledText(
            self.tab, height=10, width=70, wrap=tk.WORD, font=("Arial", 10)
        )
        self.mes_example_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore[arg-type]

        # Alternate Greetings
        ttk.Label(self.tab, text="Alternate Greetings:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.alt_greetings_text = scrolledtext.ScrolledText(
            self.tab, height=6, width=70, wrap=tk.WORD, font=("Arial", 10)
        )
        self.alt_greetings_text.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore[arg-type]

        ttk.Label(
            self.tab, text="(One greeting per line)", font=("Arial", 9), foreground="gray"
        ).grid(row=6, column=0, sticky=tk.W)

        # Configure row weights
        self.tab.columnconfigure(0, weight=1)
        for i in range(7):
            self.tab.rowconfigure(i, weight=0)

    def populate(self, data: Dict[str, Any]) -> None:
        """
        Populate form fields from character data.

        Args:
            data: Character data dictionary
        """
        from core.parser import get_actual_data

        char_data = get_actual_data(data)

        self.set_text(self.first_mes_text, char_data.get('first_mes', ''))
        self.set_text(self.mes_example_text, char_data.get('mes_example', ''))

        # Alternate greetings (array to newline-separated)
        alt_greetings = char_data.get('alternate_greetings', [])
        if isinstance(alt_greetings, list):
            self.set_text(self.alt_greetings_text, '\n'.join(alt_greetings))  # type: ignore[misc]
        else:
            self.set_text(self.alt_greetings_text, '')

        logger.debug("Messages tab populated")

    def get_data(self) -> Dict[str, Any]:
        """
        Get data from form fields.

        Returns:
            Dictionary of form field data
        """
        # Alternate greetings (newline-separated to array)
        alt_greetings_text = self.alt_greetings_text.get(1.0, tk.END).strip()
        alt_greetings = [line.strip() for line in alt_greetings_text.split('\n') if line.strip()]

        return {
            'first_mes': self.first_mes_text.get(1.0, tk.END).strip(),
            'mes_example': self.mes_example_text.get(1.0, tk.END).strip(),
            'alternate_greetings': alt_greetings
        }

    def clear(self) -> None:
        """Clear all form fields."""
        self.set_text(self.first_mes_text, '')
        self.set_text(self.mes_example_text, '')
        self.set_text(self.alt_greetings_text, '')
        logger.debug("Messages tab cleared")

    def set_text(self, text_widget: scrolledtext.ScrolledText, text: str) -> None:
        """
        Helper to set text in scrolled text widget.

        Args:
            text_widget: Text widget
            text: Text to set
        """
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, text or '')
