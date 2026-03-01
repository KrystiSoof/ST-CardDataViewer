"""Basic Info tab implementation."""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any
import logging

logger = logging.getLogger('SillyTavernCardEditor')


class BasicInfoTab:
    """Handles the Basic Info tab UI and data management."""

    def __init__(self, parent: ttk.Notebook):
        """
        Initialize the Basic Info tab.

        Args:
            parent: Parent notebook widget
        """
        self.tab = ttk.Frame(parent, padding="10")
        parent.add(self.tab, text="📝 Basic Info")

        # Form variables
        self.name_var = tk.StringVar()
        self.description_text: scrolledtext.ScrolledText = None  # type: ignore[assignment]
        self.personality_text: scrolledtext.ScrolledText = None  # type: ignore[assignment]
        self.scenario_text: scrolledtext.ScrolledText = None  # type: ignore[assignment]

        self.create_widgets()
        logger.debug("Basic Info tab initialized")

    def create_widgets(self) -> None:
        """Create all widgets for the Basic Info tab."""
        # Name
        ttk.Label(self.tab, text="Character Name:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        name_entry = ttk.Entry(self.tab, textvariable=self.name_var, width=60, font=("Arial", 11))
        name_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore[arg-type]

        # Description
        ttk.Label(self.tab, text="Description:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.description_text = scrolledtext.ScrolledText(
            self.tab, height=6, width=70, wrap=tk.WORD, font=("Arial", 10)
        )
        self.description_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore[arg-type]

        # Personality
        ttk.Label(self.tab, text="Personality:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.personality_text = scrolledtext.ScrolledText(
            self.tab, height=6, width=70, wrap=tk.WORD, font=("Arial", 10)
        )
        self.personality_text.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore[arg-type]

        # Scenario
        ttk.Label(self.tab, text="Scenario:", font=("Arial", 10, "bold")).grid(
            row=6, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.scenario_text = scrolledtext.ScrolledText(
            self.tab, height=6, width=70, wrap=tk.WORD, font=("Arial", 10)
        )
        self.scenario_text.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore[arg-type]

        # Configure row weights
        self.tab.columnconfigure(0, weight=1)
        for i in range(8):
            self.tab.rowconfigure(i, weight=0)

        # Bind text change events for validation
        self.description_text.bind("<KeyRelease>", lambda e: self.on_text_change())
        self.personality_text.bind("<KeyRelease>", lambda e: self.on_text_change())
        self.scenario_text.bind("<KeyRelease>", lambda e: self.on_text_change())

    def on_text_change(self) -> None:
        """Handle text change events."""
        # Can be used for auto-save or dirty flag
        pass

    def populate(self, data: Dict[str, Any]) -> None:
        """
        Populate form fields from character data.

        Args:
            data: Character data dictionary
        """
        from core.parser import get_actual_data

        char_data = get_actual_data(data)

        self.name_var.set(char_data.get('name', ''))
        self.set_text(self.description_text, char_data.get('description', ''))
        self.set_text(self.personality_text, char_data.get('personality', ''))
        self.set_text(self.scenario_text, char_data.get('scenario', ''))

        logger.debug("Basic Info tab populated")

    def get_data(self) -> Dict[str, Any]:
        """
        Get data from form fields.

        Returns:
            Dictionary of form field data
        """
        return {
            'name': self.name_var.get(),
            'description': self.description_text.get(1.0, tk.END).strip(),
            'personality': self.personality_text.get(1.0, tk.END).strip(),
            'scenario': self.scenario_text.get(1.0, tk.END).strip()
        }

    def clear(self) -> None:
        """Clear all form fields."""
        self.name_var.set('')
        self.set_text(self.description_text, '')
        self.set_text(self.personality_text, '')
        self.set_text(self.scenario_text, '')
        logger.debug("Basic Info tab cleared")

    def set_text(self, text_widget: scrolledtext.ScrolledText, text: str) -> None:
        """
        Helper to set text in scrolled text widget.

        Args:
            text_widget: Text widget
            text: Text to set
        """
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, text or '')
