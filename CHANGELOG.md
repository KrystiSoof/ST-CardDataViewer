# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Comprehensive MIT License
- Updated README with complete documentation
- Full type hints and Pylance compliance
- Comprehensive unit test coverage (42 tests)

### Fixed
- All Pylance type checking errors
- Proper Optional handling for nullable types
- Correct type annotations for tkinter methods

### Changed
- Modular architecture with separated core, ui, and utils packages
- Logging system replacing print statements
- Configuration file support
- Undo/redo history management
- Auto-save with configurable intervals
- Drag and drop support (optional via tkinterdnd2)

### Security
- No hardcoded paths or credentials
- User files (.png, .json) excluded from version control
- Config files excluded from version control

---

## Version 1.0.0 - Initial Release

### Features
- Visual character card preview
- Tabbed interface (Basic Info, Messages, Advanced, Raw JSON)
- Form-based editing for all character fields
- V2 (chara) and V3 (ccv3) format support
- Save changes back to PNG files
- Copy JSON to clipboard
- Format and prettify JSON
- Search and replace in JSON editor

### Data Format Support
- V2 Format (chara keyword)
- V3 Format (ccv3 keyword) - preferred
- Automatic field name detection (notes/creator_notes)
- Nested data section handling

### Supported Fields
- Name, Description, Personality, Scenario
- First Message, Example Messages, Alternate Greetings
- Creator Notes, System Prompt, Post-History Instructions
- Tags, Creator, Character Version
