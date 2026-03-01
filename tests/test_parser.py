"""Unit tests for parser module."""

import unittest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

from PIL import Image, PngImagePlugin

from core.parser import extract_sillytavern_data, get_character_format, has_nested_data


class TestParser(unittest.TestCase):
    """Test cases for the parser module."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        for file in Path(self.temp_dir).glob("*"):
            file.unlink()
        os.rmdir(self.temp_dir)

    def create_test_image(self, data: Dict[str, Any], keyword: str = "chara") -> str:
        """
        Create a test PNG image with embedded character data.

        Args:
            data: Character data to embed
            keyword: PNG keyword to use (chara or ccv3)

        Returns:
            Path to the created test image
        """
        import base64
        import json

        # Create a simple image
        img = Image.new('RGB', (100, 100), color='red')

        # Embed data
        json_str = json.dumps(data)
        base64_data = base64.b64encode(json_str.encode('utf-8')).decode('ascii')

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text(keyword, base64_data)

        # Save image
        file_path = os.path.join(self.temp_dir, f"test_{keyword}.png")
        img.save(file_path, 'PNG', pnginfo=pnginfo)

        return file_path

    def test_extract_v2_data(self):
        """Test extracting V2 character data."""
        test_data: Dict[str, Any] = {
            "name": "Test Character",
            "description": "A test character",
            "tags": ["test", "character"],
            "notes": "Test notes",
            "spec": "chara_card_v2",
            "spec_version": "2.0"
        }

        file_path = self.create_test_image(test_data, "chara")  # type: ignore[arg-type]
        result = extract_sillytavern_data(file_path)

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test Character")  # type: ignore[index]
        self.assertEqual(result["spec"], "chara_card_v2")  # type: ignore[index]

    def test_extract_v3_data(self):
        """Test extracting V3 character data."""
        test_data: Dict[str, Any] = {
            "name": "Test Character V3",
            "description": "A test V3 character",
            "tags": ["test", "v3"],
            "creator_notes": "V3 notes",
            "spec": "chara_card_v3",
            "spec_version": "3.0"
        }

        file_path = self.create_test_image(test_data, "ccv3")  # type: ignore[arg-type]
        result = extract_sillytavern_data(file_path)

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test Character V3")  # type: ignore[index]
        self.assertEqual(result["spec"], "chara_card_v3")  # type: ignore[index]

    def test_extract_no_data(self):
        """Test extracting from image without character data."""
        # Create image without embedded data
        img = Image.new('RGB', (100, 100), color='blue')
        file_path = os.path.join(self.temp_dir, "test_no_data.png")
        img.save(file_path)

        result = extract_sillytavern_data(file_path)
        self.assertIsNone(result)

    def test_get_character_format(self):
        """Test getting character format."""
        test_data = {
            "name": "Test",
            "spec": "chara_card_v3",
            "spec_version": "3.0"
        }

        spec, version = get_character_format(test_data)
        self.assertEqual(spec, "chara_card_v3")
        self.assertEqual(version, "3.0")

    def test_has_nested_data(self):
        """Test checking for nested data section."""
        test_data_with_nested: Dict[str, Any] = {
            "name": "Test",
            "data": {"name": "Test", "description": "Nested"}
        }

        test_data_without_nested: Dict[str, Any] = {
            "name": "Test",
            "description": "Direct"
        }

        self.assertTrue(has_nested_data(test_data_with_nested))  # type: ignore[arg-type]
        self.assertFalse(has_nested_data(test_data_without_nested))

    def test_v3_priority_over_v2(self):
        """Test that V3 data takes priority over V2 when both present."""
        v2_data = {
            "name": "V2 Character",
            "spec": "chara_card_v2",
            "spec_version": "2.0"
        }

        v3_data = {
            "name": "V3 Character",
            "spec": "chara_card_v3",
            "spec_version": "3.0"
        }

        # Create image with both V2 and V3 data
        import base64
        import json

        img = Image.new('RGB', (100, 100), color='green')

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text('chara', base64.b64encode(json.dumps(v2_data).encode('utf-8')).decode('ascii'))
        pnginfo.add_text('ccv3', base64.b64encode(json.dumps(v3_data).encode('utf-8')).decode('ascii'))

        file_path = os.path.join(self.temp_dir, "test_both.png")
        img.save(file_path, 'PNG', pnginfo=pnginfo)

        result = extract_sillytavern_data(file_path)

        # V3 should be returned
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "V3 Character")  # type: ignore[index]
        self.assertEqual(result["spec"], "chara_card_v3")  # type: ignore[index]


if __name__ == '__main__':
    unittest.main()
