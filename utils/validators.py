"""Data validation utilities."""

import re
from typing import List, Tuple


def validate_tags(tags_text: str) -> Tuple[bool, List[str], str]:
    """
    Validate and clean tags input.

    Args:
        tags_text: Comma-separated tags string

    Returns:
        Tuple of (is_valid, tags_list, error_message)
    """
    if not tags_text.strip():
        return True, [], ""

    tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]

    # Validate each tag
    invalid_tags: List[str] = []
    valid_tags: List[str] = []
    for tag in tags:
        if len(tag) > 100:
            invalid_tags.append(f"'{tag}' (too long, max 100 chars)")
        elif not re.match(r'^[\w\s\-]+$', tag):
            invalid_tags.append(f"'{tag}' (invalid characters)")
        else:
            valid_tags.append(tag)

    if invalid_tags:
        error = f"Invalid tags: {', '.join(invalid_tags)}"
        return False, valid_tags, error

    return True, valid_tags, ""


def validate_character_name(name: str) -> Tuple[bool, str]:
    """
    Validate character name.

    Args:
        name: Character name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name.strip():
        return False, "Character name cannot be empty"

    if len(name) > 200:
        return False, "Character name too long (max 200 characters)"

    return True, ""


def validate_text_field(text: str, field_name: str, max_length: int = 10000) -> Tuple[bool, str]:
    """
    Validate a text field.

    Args:
        text: Text content
        field_name: Name of the field for error messages
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text.strip():
        return True, ""  # Empty is allowed

    if len(text) > max_length:
        return False, f"{field_name} too long (max {max_length} characters)"

    return True, ""
