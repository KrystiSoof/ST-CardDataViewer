# SillyTavern Card Data Viewer

A powerful, easy-to-use GUI application for viewing and editing embedded SillyTavern character card data in PNG files.

## Features

### Core Functionality
- **Visual Preview**: See the character card image in the preview pane
- **Tabbed Interface**: Easy-to-use tabs for different character sections
- **Form-Based Editing**: Edit character data in friendly form fields instead of raw JSON
- **Live Sync**: Changes in form fields automatically update the raw JSON view
- **Format JSON**: Automatically format and prettify your JSON data
- **Save Changes**: Save your edits back to the original file or create a new file

### Data Editing Tabs
- **📝 Basic Info**: Edit name, description, personality, and scenario
- **💬 Messages**: Edit first message, example messages, and alternate greetings
- **⚙️ Advanced**: Edit creator notes, system prompts, tags, and metadata
- **🔧 Raw JSON**: Direct JSON editing for advanced users with search & replace

### History & Autosave
- **Undo/Redo**: Full undo/redo history with configurable size (default: 50 states)
- **Auto-Save**: Automatic saving with configurable interval (default: 5 minutes)
- **Automatic Backups**: Backup files created before each save
- **Visual Status**: Indicators for save status and operations

### File Management
- **Drag & Drop**: Drop PNG files directly into the application
- **JSON Export**: Export character data to standalone JSON files
- **JSON Import**: Import character data from JSON files
- **Batch Processing**: Process multiple character cards at once
- **Copy JSON**: Easily copy character data to clipboard

### Data Validation & Quality
- **Real-time Validation**: Validate tags, names, and text fields
- **Tag Validation**: Max 100 characters, no special characters
- **Name Validation**: Max 200 characters
- **Better Error Messages**: Clear, specific error messages for common issues
- **Loading Indicators**: Visual feedback during file operations

### Configuration
- **JSON-based Configuration**: Customize all settings in `config.json`
- **UI Settings**: Window size, fonts, colors
- **Editor Preferences**: Auto-format, word wrap, validation
- **Feature Toggles**: Enable/disable features as needed
- **Logging Options**: Configure log levels and output

## Quick Start

1. Double-click **[setup.bat](setup.bat)** to install dependencies
2. Double-click **[run.bat](run.bat)** to launch
3. Click **"📁 Browse File"** (or drag & drop) to select your character card
4. Edit data in any of the tabs
5. Click **"💾 Save Changes"** to save your edits

## Installation

### Option 1: Quick Setup (Recommended)

1. Double-click `setup.bat` to install dependencies automatically

### Option 2: Manual Setup

1. Make sure you have Python 3.8 or higher installed
2. Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

## Configuration

The application creates a `config.json` file on first run with customizable settings:

```json
{
  "ui": {
    "window_width": 1100,
    "window_height": 700,
    "preview_width": 400,
    "preview_height": 600
  },
  "autosave": {
    "enabled": true,
    "interval_minutes": 5
  },
  "features": {
    "drag_and_drop": true,
    "undo_redo": true,
    "max_history": 50
  }
}
```

See `config.json` for all available options.

## Usage

### Running the Application

**Option 1: Double-click (Recommended)**
```
Double-click run.bat
```

**Option 2: Command Line**
```bash
python main.py
```

### Editing Character Cards

1. **Load a character card**:
   - Click "📁 Browse File" button
   - OR drag and drop a PNG file onto the preview area

2. **Edit character data** using the tabbed interface:
   - **📝 Basic Info**: Name, description, personality, scenario
   - **💬 Messages**: First message, example messages, alternate greetings
   - **⚙️ Advanced**: Creator notes, system prompts, tags, metadata
   - **🔧 Raw JSON**: Direct JSON editing for advanced users

3. **Use action buttons**:
   - **📁 Browse File**: Load a new PNG file
   - **💾 Save Changes**: Save your edits to the original file
   - **Save As New File**: Create a new PNG file with your changes
   - **📋 Copy JSON**: Copy character data to clipboard
   - **🔄 Refresh**: Sync form fields from raw JSON after manual edits
   - **↩️ Undo**: Undo last change
   - **↪️ Redo**: Redo last undone change
   - **📤 Export JSON**: Export data to JSON file
   - **📥 Import JSON**: Import data from JSON file

4. **Auto-save**: Changes are automatically saved at intervals (configurable)

## Supported Data Formats

### V2 Format (chara)
- Uses `chara` keyword in PNG tEXt chunks
- Base64 encoded JSON data
- Fallback if V3 not present

### V3 Format (ccv3) - Preferred
- Uses `ccv3` keyword in PNG tEXt chunks
- Base64 encoded JSON data
- Takes precedence over V2 when both are present
- Supports nested `data` section structure

### Field Name Support
The application automatically handles various field name conventions:
- **Creator Notes**: Supports both `creator_notes` and `notes` field names
- **Structure Detection**: Automatically detects V3 format with nested `data` section
- **Backward Compatibility**: Maintains original field names when saving

## Running Tests

To run the unit tests:

```bash
# Windows
run_tests.bat

# Or using pytest directly
pytest tests/ -v
```

Test coverage includes:
- Parser functionality
- Data validation
- JSON formatting
- History management

## Requirements

- Python 3.8+
- Pillow>=10.0.0
- jsonschema>=4.0.0
- tkinterdnd2>=0.3.0 (optional, for drag and drop)
- pytest>=7.0.0 (for testing)

## Project Structure

```
ST-CardDataViewer/
├── main.py                     # Entry point
├── requirements.txt            # Dependencies
├── config.json               # Configuration (auto-created)
├── run.bat                  # Run application
├── run_tests.bat            # Run unit tests
├── setup.bat                # Install dependencies
├── core/                   # Core functionality
│   ├── parser.py           # Data extraction
│   ├── formatter.py        # JSON formatting
│   └── saver.py           # File saving
├── ui/                     # UI components
│   ├── main_window.py      # Main window
│   └── tabs/             # Tab implementations
├── utils/                  # Utilities
│   ├── validators.py       # Data validation
│   ├── config.py          # Configuration
│   ├── history.py         # Undo/redo
│   └── logger.py         # Logging
└── tests/                 # Unit tests
```

## Troubleshooting

**"Import 'PIL' could not be resolved":**
- Run `setup.bat` to install dependencies
- Or manually: `python -m pip install -r requirements.txt`

**Drag and drop not working:**
- Install `tkinterdnd2`: `pip install tkinterdnd2`
- Or disable in `config.json`: `"drag_and_drop": false`

**Auto-save not working:**
- Check `config.json`: `"autosave": {"enabled": true}`
- Ensure file has been saved at least once

**Undo/redo not available:**
- Check `config.json`: `"features": {"undo_redo": true}`
- History is cleared when loading a new file

## Tips

- Use **Undo/Redo** to experiment with changes
- **Auto-save** protects against data loss
- **Export JSON** for version control and backup
- **Validation** shows issues in real-time
- **Drag & Drop** for quick file loading
- Customize **settings** in `config.json`
- **Run tests** to verify functionality

## License

This is a utility tool for viewing and editing SillyTavern character card data. Feel free to use and modify as needed.
