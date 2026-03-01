"""File saving utilities."""

import base64
import json
import logging
import os
from typing import Optional, Dict, Any

from PIL import Image, PngImagePlugin

logger = logging.getLogger('SillyTavernCardEditor')


def save_file(
    file_path: str,
    image: Image.Image,
    data: Dict[str, Any],
    backup: bool = True,
    backup_extension: str = ".bak"
) -> tuple[bool, Optional[str]]:
    """
    Save the image with updated character data.

    Args:
        file_path: Path to save the file
        image: PIL Image object
        data: Character data to embed
        backup: Whether to create backup before saving
        backup_extension: Extension for backup file

    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Create backup if requested and file exists
        if backup and os.path.exists(file_path):
            backup_path = file_path + backup_extension
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")

        # Base64 encode JSON data (SillyTavern format)
        json_str = json.dumps(data, ensure_ascii=False)
        base64_data = base64.b64encode(json_str.encode('utf-8')).decode('ascii')

        # Create PNG info with the data
        pnginfo = PngImagePlugin.PngInfo()

        # Store as 'chara' key in tEXt chunk with Base64 encoding
        pnginfo.add_text('chara', base64_data)

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)

        # Save the image with embedded data
        image.save(file_path, 'PNG', pnginfo=pnginfo)

        logger.info(f"Successfully saved file: {file_path}")
        return True, None

    except PermissionError as e:
        error_msg = f"Permission denied: Cannot save to {file_path}\nThe file might be open in another application."
        logger.error(error_msg)
        return False, error_msg
    except OSError as e:
        error_msg = f"Failed to save file: {str(e)}\nCheck if the disk is full or the path is valid."
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error saving file: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def export_json(file_path: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Export character data to a separate JSON file.

    Args:
        file_path: Path to save the JSON file
        data: Character data to export

    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully exported JSON to: {file_path}")
        return True, None

    except Exception as e:
        error_msg = f"Failed to export JSON: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def import_json(file_path: str) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Import character data from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Tuple of (success, data, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Successfully imported JSON from: {file_path}")
        return True, data, None

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON file: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg
    except Exception as e:
        error_msg = f"Failed to import JSON: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg
