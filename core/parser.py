"""Parser for extracting SillyTavern character data from PNG files."""

import base64
import json
import logging
from typing import Dict, Optional, Tuple, Any

logger = logging.getLogger('SillyTavernCardEditor')


def extract_sillytavern_data(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract SillyTavern character data from PNG file.

    SillyTavern stores data in PNG tEXt chunks with Base64 encoding.
    Supports both V2 (chara) and V3 (ccv3) formats.

    Args:
        file_path: Path to the PNG file

    Returns:
        Parsed character data dictionary or None if not found
    """
    try:
        with open(file_path, 'rb') as f:
            # Skip PNG signature (8 bytes)
            f.read(8)

            # Store found data with priority: ccv3 (V3) > chara (V2)
            found_data = {'ccv3': None, 'chara': None}

            while True:
                # Read chunk length (4 bytes)
                length_data = f.read(4)
                if len(length_data) < 4:
                    break

                length = int.from_bytes(length_data, byteorder='big')

                # Read chunk type (4 bytes)
                chunk_type = f.read(4).decode('ascii', errors='ignore')

                # Read chunk data
                chunk_data = f.read(length)

                # Read CRC (4 bytes)
                f.read(4)

                # Check for tEXt chunks containing character data
                if chunk_type == 'tEXt':
                    # tEXt format: keyword\0data
                    parts = chunk_data.split(b'\x00', 1)
                    if len(parts) == 2:
                        keyword = parts[0].decode('ascii', errors='ignore').lower()
                        data = parts[1]

                        # Look for ccv3 (V3) or chara (V2) keywords
                        if keyword == 'ccv3':
                            try:
                                decoded_data = base64.b64decode(data).decode('utf-8')
                                found_data['ccv3'] = json.loads(decoded_data)
                                logger.info("Found V3 character data (ccv3)")
                            except Exception as e:
                                logger.warning(f"Error decoding ccv3: {e}")

                        elif keyword == 'chara':
                            try:
                                decoded_data = base64.b64decode(data).decode('utf-8')
                                found_data['chara'] = json.loads(decoded_data)
                                logger.info("Found V2 character data (chara)")
                            except Exception as e:
                                logger.warning(f"Error decoding chara: {e}")

                # Stop at IEND chunk
                if chunk_type == 'IEND':
                    break

            # Return ccv3 (V3) if available, otherwise chara (V2)
            if found_data['ccv3'] is not None:
                return found_data['ccv3']
            if found_data['chara'] is not None:
                return found_data['chara']

        return None

    except Exception as e:
        logger.error(f"Error extracting data from {file_path}: {e}")
        return None


def get_character_format(data: Dict[str, Any]) -> Tuple[str, str]:
    """
    Get the format version and structure of character data.

    Args:
        data: Character data dictionary

    Returns:
        Tuple of (spec, spec_version)
    """
    spec = data.get('spec', 'unknown')
    spec_version = data.get('spec_version', '?')
    return spec, spec_version


def has_nested_data(data: Dict[str, Any]) -> bool:
    """
    Check if character data has nested 'data' section.

    Args:
        data: Character data dictionary

    Returns:
        True if has nested data section
    """
    return 'data' in data and isinstance(data['data'], dict)


def get_actual_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the actual character data, handling nested structures.

    Args:
        data: Character data dictionary

    Returns:
        Actual character data (either direct or from nested 'data' section)
    """
    if has_nested_data(data):
        logger.debug("Using nested 'data' section")
        return data['data']
    elif 'spec' in data and 'data' in data:
        logger.debug("Using V3 format with 'data' section")
        return data.get('data', {})
    else:
        logger.debug("Using direct data (no wrapper)")
        return data
