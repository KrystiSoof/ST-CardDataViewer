"""Unit tests for validators module."""

import unittest

from utils.validators import validate_tags, validate_character_name, validate_text_field


class TestValidators(unittest.TestCase):
    """Test cases for the validators module."""

    def test_validate_tags_empty(self):
        """Test validating empty tags."""
        is_valid, tags, error = validate_tags("")
        self.assertTrue(is_valid)
        self.assertEqual(tags, [])
        self.assertEqual(error, "")

    def test_validate_tags_valid(self):
        """Test validating valid tags."""
        is_valid, tags, error = validate_tags("Kitsune, Fantasy, Magic")
        self.assertTrue(is_valid)
        self.assertEqual(tags, ["Kitsune", "Fantasy", "Magic"])
        self.assertEqual(error, "")

    def test_validate_tags_invalid_characters(self):
        """Test validating tags with invalid characters."""
        is_valid, tags, error = validate_tags("Valid Tag, Invalid@Tag, Another Valid")
        self.assertFalse(is_valid)
        self.assertIn("Invalid@Tag", error)
        self.assertEqual(len(tags), 2)  # Only valid tags returned

    def test_validate_tags_too_long(self):
        """Test validating tags that are too long."""
        long_tag = "a" * 150  # More than 100 characters
        is_valid, tags, error = validate_tags(f"ShortTag, {long_tag}")
        self.assertFalse(is_valid)
        self.assertIn("too long", error)
        self.assertEqual(len(tags), 1)  # Only the short tag

    def test_validate_tags_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        is_valid, tags, _error = validate_tags("  Tag1  ,  Tag2  ,  Tag3  ")
        self.assertTrue(is_valid)
        self.assertEqual(tags, ["Tag1", "Tag2", "Tag3"])

    def test_validate_character_name_valid(self):
        """Test validating valid character name."""
        is_valid, error = validate_character_name("Rin Caelum")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_character_name_empty(self):
        """Test validating empty character name."""
        is_valid, error = validate_character_name("")
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", error)

    def test_validate_character_name_whitespace_only(self):
        """Test validating whitespace-only character name."""
        is_valid, error = validate_character_name("   ")
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", error)

    def test_validate_character_name_too_long(self):
        """Test validating character name that is too long."""
        long_name = "a" * 250  # More than 200 characters
        is_valid, error = validate_character_name(long_name)
        self.assertFalse(is_valid)
        self.assertIn("too long", error)

    def test_validate_text_field_valid(self):
        """Test validating valid text field."""
        is_valid, error = validate_text_field("Some text here", "Description")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_text_field_empty(self):
        """Test validating empty text field."""
        is_valid, error = validate_text_field("", "Description")
        self.assertTrue(is_valid)  # Empty is allowed
        self.assertEqual(error, "")

    def test_validate_text_field_too_long(self):
        """Test validating text field that is too long."""
        long_text = "a" * 15000  # More than default 10000 characters
        is_valid, error = validate_text_field(long_text, "Description")
        self.assertFalse(is_valid)
        self.assertIn("too long", error)

    def test_validate_text_field_custom_max_length(self):
        """Test validating text field with custom max length."""
        text = "a" * 500
        is_valid, error = validate_text_field(text, "Field", max_length=100)
        self.assertFalse(is_valid)
        self.assertIn("too long", error)


if __name__ == '__main__':
    unittest.main()
