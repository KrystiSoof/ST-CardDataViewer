"""Advanced tab implementation."""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any
import logging

from utils.validators import validate_tags

logger = logging.getLogger('SillyTavernCardEditor')


class AdvancedTab:
    """Handles the Advanced tab UI and data management."""

    def __init__(self, parent: ttk.Notebook):
        """
        Initialize the Advanced tab.

        Args:
            parent: Parent notebook widget
        """
        self.tab = ttk.Frame(parent, padding="10")
        parent.add(self.tab, text="⚙️ Advanced")

        self.creator_notes_text: scrolledtext.ScrolledText = None  # type: ignore[assignment]
        self.system_prompt_text: scrolledtext.ScrolledText = None  # type: ignore[assignment]
        self.post_history_text: scrolledtext.ScrolledText = None  # type: ignore[assignment]
        self.tags_entry: ttk.Entry = None  # type: ignore[assignment]
        self.creator_entry: ttk.Entry = None  # type: ignore[assignment]
        self.version_entry: ttk.Entry = None  # type: ignore[assignment]

        self.validation_label = ttk.Label(self.tab, text="", foreground="red", font=("Arial", 9))

        self.create_widgets()
        logger.debug("Advanced tab initialized")

    def create_widgets(self) -> None:
        """Create all widgets for the Advanced tab."""
        # Creator Notes
        ttk.Label(self.tab, text="Creator Notes:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.creator_notes_text = scrolledtext.ScrolledText(
            self.tab, height=6, width=70, wrap=tk.WORD, font=("Arial", 10)
        )
        self.creator_notes_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore[arg-type]

        # System Prompt
        ttk.Label(self.tab, text="System Prompt:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.system_prompt_text = scrolledtext.ScrolledText(
            self.tab, height=4, width=70, wrap=tk.WORD, font=("Arial", 10)
        )
        self.system_prompt_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore[arg-type]

        # Post History Instructions
        ttk.Label(self.tab, text="Post-History Instructions:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.post_history_text = scrolledtext.ScrolledText(
            self.tab, height=4, width=70, wrap=tk.WORD, font=("Arial", 10)
        )
        self.post_history_text.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore[arg-type]

        # Metadata section
        metadata_frame = ttk.LabelFrame(self.tab, text="Metadata", padding="10")
        metadata_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(10, 0), padx=0)  # type: ignore[arg-type]

        # Tags
        ttk.Label(metadata_frame, text="Tags (comma separated):", font=("Arial", 9)).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.tags_entry = ttk.Entry(metadata_frame, width=60, font=("Arial", 10))
        self.tags_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))  # type: ignore[arg-type]
        self.tags_entry.bind("<KeyRelease>", lambda e: self.validate_tags())

        # Validation label
        self.validation_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        # Creator
        ttk.Label(metadata_frame, text="Creator:", font=("Arial", 9)).grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.creator_entry = ttk.Entry(metadata_frame, width=60, font=("Arial", 10))
        self.creator_entry.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))  # type: ignore[arg-type]

        # Character Version
        ttk.Label(metadata_frame, text="Character Version:", font=("Arial", 9)).grid(
            row=5, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.version_entry = ttk.Entry(metadata_frame, width=60, font=("Arial", 10))
        self.version_entry.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 5))  # type: ignore[arg-type]

        # Configure row weights
        self.tab.columnconfigure(0, weight=1)
        for i in range(7):
            self.tab.rowconfigure(i, weight=0)
        for i in range(7):
            metadata_frame.rowconfigure(i, weight=0)

    def validate_tags(self) -> None:
        """Validate tags and show validation message."""
        tags_text = self.tags_entry.get()
        is_valid, _tags, error = validate_tags(tags_text)

        if is_valid:
            self.validation_label.config(text="")
        else:
            self.validation_label.config(text=error)

    def populate(self, data: Dict[str, Any]) -> None:
        """
        Populate form fields from character data.

        Args:
            data: Character data dictionary
        """
        from core.parser import get_actual_data

        char_data = get_actual_data(data)

        # Handle both 'creator_notes' and 'notes' field names
        creator_notes = char_data.get('creator_notes') or char_data.get('notes', '')
        self.set_text(self.creator_notes_text, creator_notes)

        self.set_text(self.system_prompt_text, char_data.get('system_prompt', ''))
        self.set_text(self.post_history_text, char_data.get('post_history_instructions', ''))

        # Tags
        tags = char_data.get('tags', [])
        if isinstance(tags, list):
            tags_str = ', '.join(str(t) for t in tags)  # type: ignore[misc]
            self.tags_entry.delete(0, tk.END)
            self.tags_entry.insert(0, tags_str)
        else:
            self.tags_entry.delete(0, tk.END)

        # Creator
        creator_value = char_data.get('creator', '')
        self.creator_entry.delete(0, tk.END)
        self.creator_entry.insert(0, creator_value)

        # Version
        version_value = char_data.get('character_version', '')
        self.version_entry.delete(0, tk.END)
        self.version_entry.insert(0, version_value)

        logger.debug("Advanced tab populated")

    def get_data(self) -> Dict[str, Any]:
        """
        Get data from form fields.

        Returns:
            Dictionary of form field data
        """
        # Tags - validate before returning
        tags_text = self.tags_entry.get().strip()
        is_valid, tags, error = validate_tags(tags_text)

        if not is_valid:
            logger.warning(f"Invalid tags: {error}")
        # Return validated tags even if invalid (user might want to save anyway)

        return {
            'creator_notes': self.creator_notes_text.get(1.0, tk.END).strip(),
            'system_prompt': self.system_prompt_text.get(1.0, tk.END).strip(),
            'post_history_instructions': self.post_history_text.get(1.0, tk.END).strip(),
            'tags': tags,
            'creator': self.creator_entry.get(),
            'character_version': self.version_entry.get()
        }

    def clear(self) -> None:
        """Clear all form fields."""
        self.set_text(self.creator_notes_text, '')
        self.set_text(self.system_prompt_text, '')
        self.set_text(self.post_history_text, '')
        self.tags_entry.delete(0, tk.END)
        self.creator_entry.delete(0, tk.END)
        self.version_entry.delete(0, tk.END)
        self.validation_label.config(text="")
        logger.debug("Advanced tab cleared")

    def set_text(self, text_widget: scrolledtext.ScrolledText, text: str) -> None:
        """
        Helper to set text in scrolled text widget.

        Args:
            text_widget: Text widget
            text: Text to set
        """
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, text or '')
