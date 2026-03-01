"""
Character Card Verification Script

This script performs a comprehensive check of your character card to verify:
1. Data extraction works correctly
2. Tags and notes are present
3. Field names are properly mapped
4. Format is supported

Usage:
    python verify_character.py [character_card.png]

Example:
    python verify_character.py Rin_Caelum.png
"""

import sys
import os
import json
import base64
from typing import Dict, Any, Optional, Tuple


def extract_character_data(file_path: str) -> Optional[Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]]:
    """Extract character data from PNG file."""
    from PIL import Image

    try:
        img: Any = Image.open(file_path)  # type: ignore[assignment]
    except Exception as e:
        print(f"❌ Error opening image: {e}")
        return None

    # Look for SillyTavern character data
    char_data: Optional[Dict[str, Any]] = None
    spec: Optional[str] = None
    spec_version: Optional[str] = None

    # Use type ignore for PIL's missing text attribute in type stubs
    img_text: Dict[str, Any] = getattr(img, 'text', {})
    for key, value in img_text.items():  # type: ignore[attr-defined]
            if key in ['chara', 'ccv3']:
                try:
                    decoded_data = base64.b64decode(value).decode('utf-8')  # type: ignore[arg-type]
                    char_data = json.loads(decoded_data)

                    # Get spec info (char_data is guaranteed to be a dict here)
                    parsed_data: Dict[str, Any] = char_data  # type: ignore[assignment]
                    spec = parsed_data.get('spec', 'unknown')
                    spec_version = parsed_data.get('spec_version', 'unknown')

                    # Prioritize V3 (ccv3) over V2 (chara)
                    if key == 'ccv3':
                        break
                except Exception as e:
                    print(f"⚠️  Warning: Could not decode {key} data: {e}")

    img.close()
    return char_data, spec, spec_version

def verify_tags(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify tags field exists and is correct format."""
    print("\n🏷️  Tags Verification:")

    # Get data from nested section if present
    char_data = data.get('data', data) if 'data' in data else data

    if 'tags' in char_data:
        tags: list[Any] = char_data['tags']
        print(f"✅ 'tags' field found")
        print(f"   Type: {type(tags)}")
        print(f"   Value: {tags}")

        if isinstance(tags, list):  # type: ignore[unreachable]
            if len(tags) > 0:
                print(f"✅ Tags is a non-empty list")
                print(f"   Count: {len(tags)} tags")

                # Test conversion to comma-separated string
                tags_str = ', '.join(str(t) for t in tags)  # type: ignore[misc]
                print(f"✅ Tags can be joined as comma-separated:")
                print(f"   '{tags_str[:100]}...'")

                return True, tags_str
            else:
                print(f"⚠️  Tags is an empty list")
                return False, ""
        else:
            print(f"❌ Tags is not a list (found {type(tags)})")
            return False, ""
    else:
        print(f"❌ 'tags' field NOT found in character data")
        return False, ""

def verify_notes(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify notes field exists and is correct format."""
    print("\n📝 Notes Verification:")

    # Get data from nested section if present
    char_data = data.get('data', data) if 'data' in data else data

    # Check both field names
    notes_field: Optional[str] = None
    notes_value: Optional[str] = None

    if 'creator_notes' in char_data:
        notes_field = 'creator_notes'
        notes_value = char_data['creator_notes']  # type: ignore[index]
        print(f"✅ 'creator_notes' field found")
    elif 'notes' in char_data:
        notes_field = 'notes'
        notes_value = char_data['notes']  # type: ignore[index]
        print(f"✅ 'notes' field found (will map to creator_notes)")
    else:
        print(f"❌ Neither 'creator_notes' nor 'notes' field found")
        return False, ""

    notes_field = notes_field or 'unknown'
    notes_value = notes_value or ''
    print(f"   Field name: {notes_field}")
    print(f"   Value: {notes_value}")
    print(f"   Length: {len(notes_value)} characters")

    if len(notes_value) > 0:
        print(f"✅ Notes is not empty")
        return True, notes_value
    else:
        print(f"⚠️  Notes is empty")
        return False, ""

def verify_format(data: Dict[str, Any], spec: str, spec_version: str) -> bool:
    """Verify character card format."""
    print(f"\n📋 Format Verification:")

    has_nested_data = 'data' in data
    print(f"Format spec: {spec}")
    print(f"Spec version: {spec_version}")
    print(f"Has nested 'data' section: {'Yes' if has_nested_data else 'No'}")

    # Check format consistency
    if spec == 'chara_card_v3':
        print(f"✅ V3 format detected")
        if has_nested_data:
            print(f"⚠️  Note: V3 format typically doesn't use nested 'data' section")
    elif spec == 'chara_card_v2':
        print(f"✅ V2 format detected")
        if has_nested_data:
            print(f"⚠️  Note: V2 format typically doesn't use nested 'data' section")
    else:
        print(f"⚠️  Unknown format spec")

    return has_nested_data

def main():
    """Main verification routine."""
    print("=" * 70)
    print("SillyTavern Character Card Verification")
    print("=" * 70)

    # Get file path
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default to Rin_Caelum.png if not specified
        file_path = "Rin_Caelum.png"
        print(f"\n⚠️  No file specified, using default: {file_path}")

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"\n❌ Error: File not found: {file_path}")
        print(f"\nUsage: python verify_character.py [character_card.png]")
        return

    print(f"\n📂 Verifying: {file_path}")

    # Extract character data
    result = extract_character_data(file_path)
    if not result:
        print(f"\n❌ No character data found in file")
        return

    data, spec, spec_version = result

    if not data:
        print(f"\n❌ Failed to extract character data")
        return

    print(f"\n✅ Character data extracted successfully!")

    # Verify format (with defaults for None values)
    verify_format(data, spec or 'unknown', spec_version or '?')

    # Verify tags
    tags_ok, tags_str = verify_tags(data)

    # Verify notes
    notes_ok, notes_value = verify_notes(data)

    # Summary
    print("\n" + "=" * 70)
    print("📊 Summary:")
    print("=" * 70)
    print(f"Format: {spec or 'unknown'} v{spec_version or '?'}")
    print(f"Tags: {'✅ Present' if tags_ok else '❌ Missing/Empty'}")
    print(f"Notes: {'✅ Present' if notes_ok else '❌ Missing/Empty'}")

    if tags_ok and notes_ok:
        print("\n✅ All checks passed! Your character card should work correctly.")
        print("\n📝 What to expect in the application:")
        print(f"   - Tags will appear in: ⚙️ Advanced tab → Metadata → Tags field")
        print(f"   - Notes will appear in: ⚙️ Advanced tab → Creator Notes field")
        print(f"   - Tags display as: '{tags_str[:50]}...'")
        print(f"   - Notes display as: '{notes_value[:50]}...'")
    else:
        print("\n⚠️  Some fields are missing or empty:")
        if not tags_ok:
            print("   - Tags: Missing or empty")
        if not notes_ok:
            print("   - Notes: Missing or empty")
        print("\n💡 This is normal if your character card doesn't include these fields.")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
