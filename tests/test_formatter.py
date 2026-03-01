"""Unit tests for formatter module."""

import unittest

from core.formatter import format_json, remove_json_comments, validate_json


class TestFormatter(unittest.TestCase):
    """Test cases for the formatter module."""

    def test_format_json_valid(self):
        """Test formatting valid JSON."""
        json_str = '{"name":"Test","description":"A test"}'
        result = format_json(json_str, indent=2)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertIn('  "name": "Test"', result)  # type: ignore[arg-type]
        self.assertIn('  "description": "A test"', result)  # type: ignore[arg-type]

    def test_format_json_already_formatted(self):
        """Test formatting already formatted JSON."""
        json_str = '{\n  "name": "Test"\n}'
        result = format_json(json_str)

        self.assertIsNotNone(result)
        # Should still be valid
        import json
        parsed = json.loads(result)  # type: ignore[arg-type]
        self.assertEqual(parsed["name"], "Test")

    def test_format_json_invalid(self):
        """Test formatting invalid JSON."""
        json_str = '{"name": "Test", invalid}'
        result = format_json(json_str)

        self.assertIsNone(result)

    def test_format_json_empty(self):
        """Test formatting empty JSON."""
        result = format_json("")

        self.assertIsNone(result)

    def test_format_json_with_unicode(self):
        """Test formatting JSON with unicode characters."""
        json_str = '{"name":"Rin Caelum","description":"狐の女巫"}'
        result = format_json(json_str, ensure_ascii=False)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertIn("狐の女巫", result)  # type: ignore[arg-type]

    def test_remove_json_comments_line_only(self):
        """Test removing line-only comments."""
        json_str = '{"name": "Test"\n# This is a comment\n"value": 123}'
        result = remove_json_comments(json_str)

        self.assertNotIn("# This is a comment", result)
        self.assertIn('"name": "Test"', result)
        self.assertIn('"value": 123', result)

    def test_remove_json_comments_inline(self):
        """Test removing inline comments."""
        json_str = '{"name": "Test", # inline comment\n"value": 123}'
        result = remove_json_comments(json_str)

        self.assertNotIn("# inline comment", result)
        self.assertIn('"name": "Test"', result)

    def test_remove_json_comments_preserve_strings(self):
        """Test that comments in strings are preserved."""
        json_str = '{"text": "This # is not a comment"}'
        result = remove_json_comments(json_str)

        self.assertIn('"text": "This # is not a comment"', result)

    def test_validate_json_valid(self):
        """Test validating valid JSON."""
        json_str = '{"name": "Test", "value": 123}'
        is_valid, error, data = validate_json(json_str)

        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["name"], "Test")  # type: ignore[index]

    def test_validate_json_invalid(self):
        """Test validating invalid JSON."""
        json_str = '{"name": "Test", invalid}'
        is_valid, error, data = validate_json(json_str)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIsNone(data)

    def test_validate_json_with_comments(self):
        """Test validating JSON with comments."""
        json_str = '{\n  "name": "Test"\n  # Comment\n}'
        is_valid, _error, data = validate_json(json_str)

        self.assertTrue(is_valid)
        self.assertIsNone(_error)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["name"], "Test")  # type: ignore[index]

    def test_validate_json_empty(self):
        """Test validating empty string."""
        is_valid, error, _data = validate_json("")

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_format_json_different_indent(self):
        """Test formatting with different indentation."""
        json_str = '{"name": "Test"}'

        result_2 = format_json(json_str, indent=2)
        result_4 = format_json(json_str, indent=4)

        self.assertIsNotNone(result_2)
        self.assertIsInstance(result_2, str)
        self.assertIn('  "name"', result_2)  # type: ignore[arg-type]

        self.assertIsNotNone(result_4)
        self.assertIsInstance(result_4, str)
        self.assertIn('    "name"', result_4)  # type: ignore[arg-type]


if __name__ == '__main__':
    unittest.main()
