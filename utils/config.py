"""Configuration management for the application."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Manages application configuration."""

    DEFAULT_CONFIG: Dict[str, Dict[str, Any]] = {
        "ui": {
            "theme": "default",
            "window_width": 1100,
            "window_height": 700,
            "preview_width": 400,
            "preview_height": 600
        },
        "editor": {
            "auto_format_json": True,
            "show_line_numbers": False,
            "font_family": "Consolas",
            "font_size": 10,
            "wrap_word": True
        },
        "file": {
            "default_export_format": "png",
            "backup_before_save": True,
            "backup_extension": ".bak"
        },
        "autosave": {
            "enabled": True,
            "interval_minutes": 5,
            "max_backups": 10
        },
        "logging": {
            "level": "INFO",
            "log_to_file": False,
            "log_file": "sillytavern_editor.log"
        },
        "features": {
            "drag_and_drop": True,
            "undo_redo": True,
            "max_history": 50
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file. If None, uses default location.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.load()

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Try to create config in the same directory as the script
        script_dir = Path(__file__).parent.parent
        return str(script_dir / "config.yaml")

    def load(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            # Create default config file
            self.save()
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # Merge with defaults
                self._merge_config(self.config, loaded_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config file, using defaults: {e}")

    def save(self) -> None:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save config file: {e}")

    def _merge_config(self, base: Dict[str, Any], new: Dict[str, Any]) -> None:
        """Recursively merge new configuration into base configuration."""
        for key, value in new.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)  # type: ignore[arg-type]
            else:
                base[key] = value

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value by nested keys.

        Args:
            *keys: Nested keys to traverse
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, *keys: str, value: Any) -> None:
        """
        Set a configuration value by nested keys.

        Args:
            *keys: Nested keys to traverse
            value: Value to set
        """
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save()
