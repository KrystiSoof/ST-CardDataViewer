"""Main window implementation for SillyTavern Card Editor."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Any
import os

from PIL import Image, ImageTk

from core.parser import extract_sillytavern_data, get_character_format, has_nested_data
from core.saver import save_file, export_json, import_json
from utils.config import Config
from utils.history import HistoryManager
from utils.validators import validate_character_name
from utils.logger import setup_logger

from ui.tabs.basic_info_tab import BasicInfoTab
from ui.tabs.messages_tab import MessagesTab
from ui.tabs.advanced_tab import AdvancedTab
from ui.tabs.raw_json_tab import RawJsonTab

logger = setup_logger('SillyTavernCardEditor')


class SillyTavernCardEditor:
    """Main application window for SillyTavern Card Editor."""

    def __init__(self, root: tk.Tk, config_path: Optional[str] = None):
        """
        Initialize the main window.

        Args:
            root: Tkinter root window
            config_path: Optional path to configuration file
        """
        self.root = root
        self.root.title("SillyTavern Card Editor")

        # Load configuration
        self.config = Config(config_path)

        # Set window size from config
        width = self.config.get('ui', 'window_width', default=1100)
        height = self.config.get('ui', 'window_height', default=700)
        self.root.geometry(f"{width}x{height}")

        # State
        self.current_file: Optional[str] = None
        self.current_image: Optional[Image.Image] = None
        self.current_data: Optional[Dict[str, Any]] = None
        self.dirty: bool = False
        self.auto_save_timer: Optional[str] = None

        # History manager for undo/redo
        self.history = HistoryManager(
            max_history=self.config.get('features', 'max_history', default=50)
        )

        # Setup UI
        self.setup_ui()

        # Initialize drag and drop if enabled
        if self.config.get('features', 'drag_and_drop', default=True):
            self.setup_drag_and_drop()

        logger.info("SillyTavern Card Editor initialized")

    def setup_ui(self) -> None:
        """Set up the main UI components."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")  # type: ignore
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore[arg-type]

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)  # type: ignore
        self.root.rowconfigure(0, weight=1)  # type: ignore
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(1, weight=1)

        # Left side: Image preview and buttons
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))  # type: ignore[arg-type]
        left_frame.columnconfigure(0, weight=1)

        # Image preview area
        preview_frame = ttk.LabelFrame(left_frame, text="Character Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        canvas_width = self.config.get('ui', 'preview_width', default=400)
        canvas_height = self.config.get('ui', 'preview_height', default=600)

        self.image_canvas = tk.Canvas(preview_frame, width=canvas_width, height=canvas_height, bg="#f0f0f0")
        self.image_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore[arg-type]

        self.drop_label = tk.Label(
            self.image_canvas,
            text="Click to Browse\nfor PNG File",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.image_canvas.create_window(canvas_width // 2, canvas_height // 2, window=self.drop_label)
        self.image_canvas.bind("<Button-1>", self.browse_file)

        # Action buttons
        button_frame = ttk.LabelFrame(left_frame, text="Actions", padding="10")
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="📁 Browse File", command=self.browse_file, width=20).pack(pady=5)
        ttk.Button(button_frame, text="💾 Save Changes", command=self.save_changes, width=20).pack(pady=5)
        ttk.Button(button_frame, text="Save As New File", command=self.save_as, width=20).pack(pady=5)
        ttk.Button(button_frame, text="📋 Copy JSON", command=self.copy_json, width=20).pack(pady=5)
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_data, width=20).pack(pady=5)

        # Additional features
        extra_frame = ttk.LabelFrame(left_frame, text="Extra Features", padding="10")
        extra_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(extra_frame, text="📤 Export JSON", command=self.export_json_file, width=20).pack(pady=5)
        ttk.Button(extra_frame, text="📥 Import JSON", command=self.import_json_file, width=20).pack(pady=5)

        # Undo/Redo buttons if enabled
        if self.config.get('features', 'undo_redo', default=True):
            ttk.Button(extra_frame, text="↩️ Undo", command=self.undo, width=9).pack(pady=5, side=tk.LEFT, padx=2)
            ttk.Button(extra_frame, text="↪️ Redo", command=self.redo, width=9).pack(pady=5, side=tk.LEFT, padx=2)

        # Right side: Tabbed data editor
        data_frame = ttk.LabelFrame(main_frame, text="Character Data", padding="10")
        data_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore[arg-type]
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(data_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore[arg-type]

        # Create tabs
        self.basic_info_tab = BasicInfoTab(self.notebook)
        self.messages_tab = MessagesTab(self.notebook)
        self.advanced_tab = AdvancedTab(self.notebook)
        self.raw_json_tab = RawJsonTab(self.notebook)

        # Bind tab change events
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Status bar
        self.status_var = tk.StringVar(value="Ready - Browse a SillyTavern character card PNG file")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))  # type: ignore[arg-type]

    def setup_drag_and_drop(self) -> None:
        """Setup drag and drop functionality if available."""
        try:
            from tkinterdnd2 import TkinterDnD, DND_FILES  # type: ignore

            # Reinitialize root with drag and drop support
            self.root.destroy()  # type: ignore
            self.root = TkinterDnD.Tk()  # type: ignore
            self.root.title("SillyTavern Card Editor")  # type: ignore

            width = self.config.get('ui', 'window_width', default=1100)
            height = self.config.get('ui', 'window_height', default=700)
            self.root.geometry(f"{width}x{height}")  # type: ignore

            self.setup_ui()

            self.image_canvas.drop_target_register(DND_FILES)  # type: ignore
            self.image_canvas.dnd_bind('<<Drop>>', self.on_drop)  # type: ignore

            logger.info("Drag and drop enabled")
        except ImportError:
            logger.warning("tkinterdnd2 not available, drag and drop disabled")

    def on_drop(self, event: Any) -> None:
        """Handle file drop event."""
        try:
            files = self.root.splitlist(event.data)  # type: ignore
            if files:
                self.load_file(files[0])  # type: ignore
        except Exception as e:
            logger.error(f"Error handling drop: {e}")

    def browse_file(self, event: Any = None) -> None:
        """Open file browser to select PNG file."""
        file_path = filedialog.askopenfilename(
            title="Select SillyTavern Character Card",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str) -> None:
        """
        Load and parse the PNG file.

        Args:
            file_path: Path to the PNG file
        """
        try:
            self.status_var.set("Loading...")
            self.root.update()  # type: ignore

            self.current_file = file_path

            # Load image
            self.current_image = Image.open(file_path)

            # Display image
            self.display_image(self.current_image)

            # Extract SillyTavern data
            data = extract_sillytavern_data(file_path)

            if data:
                # Store the parsed data
                self.current_data = data

                spec, spec_version = get_character_format(data)
                nested = has_nested_data(data)

                logger.info(f"Loaded character data from: {os.path.basename(file_path)}")
                logger.info(f"Format: {spec} v{spec_version}")
                logger.info(f"Structure: V3 with nested 'data' section" if nested else "Standard structure")

                # Format and display JSON data in Raw JSON tab
                self.raw_json_tab.populate(data)

                # Populate form fields
                self.populate_form_fields(data)

                # Add to history
                self.history.clear()
                self.history.push_state(data)

                self.dirty = False
                self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
            else:
                self.raw_json_tab.clear()
                self.clear_form_fields()
                messagebox.showwarning("Warning", "No SillyTavern data found in this PNG file.")
                self.status_var.set("No SillyTavern data found")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
            logger.error(f"Error loading file: {e}", exc_info=True)
            self.status_var.set(f"Error: {str(e)}")

    def display_image(self, image: Image.Image) -> None:
        """
        Display the image on the canvas, scaled to fit.

        Args:
            image: PIL Image object
        """
        canvas_width = self.config.get('ui', 'preview_width', default=400)
        canvas_height = self.config.get('ui', 'preview_height', default=600)

        img_width, img_height = image.size

        # Calculate scale factor
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y)

        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        # Resize image for display
        display_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(display_image)

        # Update canvas
        self.image_canvas.delete("all")
        self.image_canvas.create_image(  # type: ignore
            canvas_width // 2,
            canvas_height // 2,
            image=self.photo,
            anchor=tk.CENTER
        )

        # Remove drop label if present
        try:
            self.drop_label.destroy()
        except:
            pass

    def populate_form_fields(self, data: Dict[str, Any]) -> None:
        """
        Populate all form fields from character data.

        Args:
            data: Character data dictionary
        """
        self.basic_info_tab.populate(data)
        self.messages_tab.populate(data)
        self.advanced_tab.populate(data)

    def clear_form_fields(self) -> None:
        """Clear all form fields."""
        self.basic_info_tab.clear()
        self.messages_tab.clear()
        self.advanced_tab.clear()

    def get_data_from_form(self) -> Optional[Dict[str, Any]]:
        """
        Collect data from all form fields.

        Returns:
            Combined data dictionary or None if validation fails
        """
        try:
            # Initialize data structure
            if self.current_data is None:
                self.current_data = {
                    'spec': 'chara_card_v2',
                    'spec_version': '2.0',
                    'data': {}
                }

            # Ensure data section exists
            if 'data' not in self.current_data:
                self.current_data['data'] = {}

            data = self.current_data['data']  # type: ignore

            # Get data from all tabs
            basic_data = self.basic_info_tab.get_data()
            messages_data = self.messages_tab.get_data()
            advanced_data = self.advanced_tab.get_data()

            # Validate character name
            is_valid, error = validate_character_name(basic_data['name'])
            if not is_valid:
                if not messagebox.askyesno(
                    "Validation Warning",
                    f"Character name validation failed:\n{error}\n\nContinue anyway?"
                ):
                    return None

            # Merge data
            data.update(basic_data)  # type: ignore
            data.update(messages_data)  # type: ignore
            data.update(advanced_data)  # type: ignore

            # Preserve original field name (notes vs creator_notes)
            if 'notes' in data and 'creator_notes' not in data:
                data['notes'] = data.pop('creator_notes')  # type: ignore

            # Update Raw JSON tab
            self.raw_json_tab.populate(self.current_data)

            self.dirty = True

            return self.current_data

        except Exception as e:
            logger.error(f"Error collecting form data: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to collect form data:\n{str(e)}")
            return None

    def copy_json(self) -> None:
        """Copy JSON data to clipboard."""
        try:
            data = self.get_data_from_form()

            if data:
                import json
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                self.root.clipboard_clear()  # type: ignore
                self.root.clipboard_append(json_str)  # type: ignore
                messagebox.showinfo("Success", "JSON copied to clipboard!")
                logger.info("JSON copied to clipboard")
            else:
                messagebox.showerror("Error", "No data to copy.")
        except Exception as e:
            logger.error(f"Error copying JSON: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to copy JSON:\n{str(e)}")

    def refresh_data(self) -> None:
        """Refresh form fields from raw JSON."""
        try:
            data = self.raw_json_tab.get_data()

            if data is None:
                messagebox.showerror("Error", "No valid JSON data to refresh from.")
                return

            self.current_data = data
            self.populate_form_fields(data)

            # Add to history
            self.history.push_state(data)

            messagebox.showinfo("Success", "Form fields refreshed from raw JSON!")
            logger.info("Form fields refreshed from raw JSON")

        except Exception as e:
            logger.error(f"Error refreshing data: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to refresh:\n{str(e)}")

    def save_changes(self) -> None:
        """Save the edited data back to the current file."""
        if not self.current_file:
            messagebox.showwarning("Warning", "No file loaded.")
            return

        if messagebox.askyesno(
            "Confirm",
            "This will overwrite the original file. Continue?"
        ):
            self.save_file(self.current_file)

    def save_as(self) -> None:
        """Save the edited data to a new file."""
        if not self.current_file:
            messagebox.showwarning("Warning", "No file loaded.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )

        if file_path:
            self.save_file(file_path)

    def save_file(self, file_path: str) -> None:
        """
        Save the current image with updated character data.

        Args:
            file_path: Path to save the file
        """
        try:
            # Get current data from form fields
            data = self.get_data_from_form()

            if data is None:
                return

            # Get backup settings
            backup = self.config.get('file', 'backup_before_save', default=True)
            backup_ext = self.config.get('file', 'backup_extension', default='.bak')

            # Ensure we have an image
            if self.current_image is None:
                messagebox.showerror("Error", "No image loaded to save")
                return

            # Save file
            success, error = save_file(file_path, self.current_image, data, backup, backup_ext)

            if success:
                self.current_file = file_path
                self.dirty = False
                self.status_var.set(f"Saved: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "File saved successfully!")
                logger.info(f"File saved: {file_path}")
            else:
                messagebox.showerror("Error", error)

        except Exception as e:
            logger.error(f"Error saving file: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def export_json_file(self) -> None:
        """Export character data to a JSON file."""
        if not self.current_data:
            messagebox.showwarning("Warning", "No data to export.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export JSON",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if file_path:
            success, error = export_json(file_path, self.current_data)
            if success:
                messagebox.showinfo("Success", "JSON exported successfully!")
            else:
                messagebox.showerror("Error", error)

    def import_json_file(self) -> None:
        """Import character data from a JSON file."""
        file_path = filedialog.askopenfilename(
            title="Import JSON",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if file_path:
            success, data, error = import_json(file_path)
            if success and data:
                self.current_data = data
                self.populate_form_fields(data)
                self.raw_json_tab.populate(data)
                self.history.push_state(data)
                self.dirty = True
                self.status_var.set(f"Imported: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "JSON imported successfully!")
            else:
                messagebox.showerror("Error", error)

    def undo(self) -> None:
        """Undo last change."""
        if not self.history.can_undo():
            messagebox.showinfo("Info", "Nothing to undo.")
            return

        data = self.history.undo()
        if data:
            self.current_data = data
            self.populate_form_fields(data)
            self.raw_json_tab.populate(data)
            self.dirty = True
            self.status_var.set("Undo performed")
            logger.info("Undo performed")

    def redo(self) -> None:
        """Redo last undone change."""
        if not self.history.can_redo():
            messagebox.showinfo("Info", "Nothing to redo.")
            return

        data = self.history.redo()
        if data:
            self.current_data = data
            self.populate_form_fields(data)
            self.raw_json_tab.populate(data)
            self.dirty = True
            self.status_var.set("Redo performed")
            logger.info("Redo performed")

    def on_tab_changed(self, event: Any) -> None:
        """Handle tab change events."""
        # When switching from form tabs to Raw JSON, sync data
        current_tab = self.notebook.index(self.notebook.select())  # type: ignore
        if current_tab == 3:  # Raw JSON tab
            self.get_data_from_form()

        # Check if auto-save is enabled
        if self.config.get('autosave', 'enabled', default=True) and self.dirty:
            self.start_auto_save_timer()

    def start_auto_save_timer(self) -> None:
        """Start the auto-save timer."""
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)  # type: ignore

        interval_minutes = self.config.get('autosave', 'interval_minutes', default=5)
        interval_ms = interval_minutes * 60 * 1000

        self.auto_save_timer = self.root.after(interval_ms, self.auto_save)  # type: ignore
        logger.debug(f"Auto-save timer started ({interval_minutes} minutes)")

    def auto_save(self) -> None:
        """Perform auto-save if dirty."""
        if self.dirty and self.current_file:
            try:
                data = self.get_data_from_form()
                if data and self.current_image:
                    backup = self.config.get('file', 'backup_before_save', default=True)
                    backup_ext = self.config.get('file', 'backup_extension', default='.bak')
                    save_file(self.current_file, self.current_image, data, backup, backup_ext)
                    self.dirty = False
                    self.status_var.set(f"Auto-saved: {os.path.basename(self.current_file)}")
                    logger.info(f"Auto-saved: {self.current_file}")
            except Exception as e:
                logger.error(f"Auto-save failed: {e}", exc_info=True)
