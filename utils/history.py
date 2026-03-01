"""History manager for undo/redo functionality."""

import json
from typing import Dict, List, Optional, Any


class HistoryManager:
    """Manages undo/redo history for data changes."""

    def __init__(self, max_history: int = 50):
        """
        Initialize history manager.

        Args:
            max_history: Maximum number of states to keep in history
        """
        self.history: List[str] = []
        self.pointer: int = -1
        self.max_history: int = max_history

    def push_state(self, data: Dict[str, Any]) -> None:
        """
        Push a new state to the history.

        Args:
            data: Data to save as a state
        """
        # Remove all states after current pointer (including current)
        self.history = self.history[:self.pointer + 1]

        # Serialize and add new state
        self.history.append(json.dumps(data, ensure_ascii=False))

        # Move pointer to the new state
        self.pointer = len(self.history) - 1

        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            # Pointer stays at the same index since we removed from front
            self.pointer = min(self.pointer, len(self.history) - 1)

    def undo(self) -> Optional[Dict[str, Any]]:
        """
        Undo to previous state.

        Returns:
            Previous state data or None if no history
        """
        if self.pointer > 0:
            self.pointer -= 1
            return json.loads(self.history[self.pointer])
        return None

    def redo(self) -> Optional[Dict[str, Any]]:
        """
        Redo to next state.

        Returns:
            Next state data or None if at end of history
        """
        if self.pointer < len(self.history) - 1:
            self.pointer += 1
            return json.loads(self.history[self.pointer])
        return None

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self.pointer >= 0 and len(self.history) > 0

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self.pointer < len(self.history) - 1

    def clear(self) -> None:
        """Clear all history."""
        self.history = []
        self.pointer = -1

    def get_current_state(self) -> Optional[Dict[str, Any]]:
        """
        Get current state.

        Returns:
            Current state data or None if no history
        """
        if self.pointer >= 0 and self.pointer < len(self.history):
            return json.loads(self.history[self.pointer])
        return None
