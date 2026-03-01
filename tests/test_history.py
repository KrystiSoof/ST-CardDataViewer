"""Unit tests for history module."""

import unittest

from utils.history import HistoryManager


class TestHistoryManager(unittest.TestCase):
    """Test cases for the HistoryManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.history = HistoryManager(max_history=5)

    def test_initial_state(self):
        """Test initial state of history manager."""
        self.assertFalse(self.history.can_undo())
        self.assertFalse(self.history.can_redo())
        self.assertIsNone(self.history.get_current_state())

    def test_push_state(self):
        """Test pushing a state to history."""
        state = {"name": "Test", "data": "value"}
        self.history.push_state(state)

        self.assertTrue(self.history.can_undo())
        self.assertFalse(self.history.can_redo())
        self.assertEqual(self.history.get_current_state(), state)

    def test_undo(self):
        """Test undo functionality."""
        state1 = {"name": "State 1"}
        state2 = {"name": "State 2"}

        self.history.push_state(state1)
        self.history.push_state(state2)

        # Undo to state1
        result = self.history.undo()
        self.assertEqual(result, state1)
        self.assertTrue(self.history.can_redo())

    def test_undo_no_history(self):
        """Test undo when no history."""
        result = self.history.undo()
        self.assertIsNone(result)

    def test_redo(self):
        """Test redo functionality."""
        state1 = {"name": "State 1"}
        state2 = {"name": "State 2"}

        self.history.push_state(state1)
        self.history.push_state(state2)
        self.history.undo()

        # Redo to state2
        result = self.history.redo()
        self.assertEqual(result, state2)
        self.assertFalse(self.history.can_redo())

    def test_redo_no_future(self):
        """Test redo when no future states."""
        state1 = {"name": "State 1"}
        self.history.push_state(state1)

        result = self.history.redo()
        self.assertIsNone(result)

    def test_push_clears_redo_history(self):
        """Test that pushing a state clears redo history."""
        state1 = {"name": "State 1"}
        state2 = {"name": "State 2"}
        state3 = {"name": "State 3"}

        self.history.push_state(state1)
        self.history.push_state(state2)
        self.history.undo()

        # Now push state3, should clear redo history
        self.history.push_state(state3)

        self.assertFalse(self.history.can_redo())
        self.assertEqual(self.history.get_current_state(), state3)

    def test_max_history_limit(self):
        """Test that history respects max limit."""
        for i in range(10):
            self.history.push_state({"state": i})

        # Should only have 5 states (max_history)
        self.assertEqual(len(self.history.history), 5)

        # Current state should be the last one pushed
        current = self.history.get_current_state()
        self.assertEqual(current["state"], 9)  # type: ignore[index]

    def test_clear_history(self):
        """Test clearing history."""
        self.history.push_state({"name": "State 1"})
        self.history.push_state({"name": "State 2"})

        self.history.clear()

        self.assertFalse(self.history.can_undo())
        self.assertFalse(self.history.can_redo())
        self.assertIsNone(self.history.get_current_state())

    def test_multiple_undo_redo(self):
        """Test multiple undo and redo operations."""
        states = [{"state": i} for i in range(5)]

        for state in states:
            self.history.push_state(state)

        # Undo all the way (from state 4 back to state 0)
        for i in range(3, -1, -1):
            result = self.history.undo()
            self.assertEqual(result["state"], i)  # type: ignore[index]

        # Redo all the way (from state 0 to state 4)
        for i in range(1, 5):
            result = self.history.redo()
            self.assertEqual(result["state"], i)  # type: ignore[index]


if __name__ == '__main__':
    unittest.main()
