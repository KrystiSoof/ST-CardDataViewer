"""JSON formatting utilities."""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('SillyTavernCardEditor')


def format_json(json_text: str, indent: int = 2, ensure_ascii: bool = False) -> Optional[str]:
    """
    Format JSON text with proper indentation.

    Args:
        json_text: JSON string to format
        indent: Number of spaces for indentation
        ensure_ascii: Whether to escape non-ASCII characters

    Returns:
        Formatted JSON string or None if invalid
    """
    try:
        # Remove comments (non-standard but common)
        cleaned_text = remove_json_comments(json_text)

        if not cleaned_text.strip():
            return None

        data = json.loads(cleaned_text)

        # Format with proper indentation
        formatted = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        return formatted

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON during formatting: {e}")
        return None
    except Exception as e:
        logger.error(f"Error formatting JSON: {e}")
        return None


def remove_json_comments(json_text: str) -> str:
    """
    Remove comments from JSON text.

    Args:
        json_text: JSON string possibly containing comments

    Returns:
        Cleaned JSON string
    """
    lines: list[str] = []
    for line in json_text.split('\n'):
        # Skip comment-only lines
        stripped = line.strip()
        if stripped.startswith('#'):
            continue

        # Remove inline comments
        if '#' in line and not line.strip().startswith('#'):
            # Only remove # if it's not inside a string
            in_string = False
            for i, char in enumerate(line):
                if char == '"':
                    in_string = not in_string
                elif char == '#' and not in_string:
                    line = line[:i]
                    break
            lines.append(line)
        else:
            lines.append(line)

    return '\n'.join(lines)


def validate_json(json_text: str) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate JSON text and parse it.

    Args:
        json_text: JSON string to validate

    Returns:
        Tuple of (is_valid, error_message, parsed_data)
    """
    try:
        cleaned_text = remove_json_comments(json_text)
        data = json.loads(cleaned_text)
        return True, None, data
    except json.JSONDecodeError as e:
        return False, str(e), None
    except Exception as e:
        return False, str(e), None
