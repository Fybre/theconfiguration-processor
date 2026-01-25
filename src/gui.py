"""Graphical user interface for Therefore Configuration Processor."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import webbrowser
import json

from .parser import ConfigurationParser
from .generator import HTMLGenerator


class ConfigProcessorGUI:
    """Main GUI application class."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Therefore Configuration Processor")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        # Variables
        self.input_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=str(Path.cwd() / "output"))
        self.title = tk.StringVar(value="Therefore Configuration")
        self.status = tk.StringVar(value="Ready")
        self.progress = tk.DoubleVar(value=0)

        # Recent files storage
        self.recent_files = []
        self.config_file = Path.home() / ".theconfiguration_processor.json"
        self._load_recent_files()

        # Build UI
        self._create_widgets()

    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Therefore Configuration Processor",
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Input file section
        input_frame = ttk.LabelFrame(main_frame, text="Input Configuration", padding="5")
        input_frame.pack(fill=tk.X, pady=5)

        input_entry = ttk.Entry(input_frame, textvariable=self.input_path, width=50)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_btn = ttk.Button(
            input_frame,
            text="Browse...",
            command=self._browse_input
        )
        browse_btn.pack(side=tk.LEFT)

        # Recent files dropdown
        if self.recent_files:
            recent_frame = ttk.Frame(main_frame)
            recent_frame.pack(fill=tk.X, pady=2)

            ttk.Label(recent_frame, text="Recent:").pack(side=tk.LEFT)

            recent_combo = ttk.Combobox(
                recent_frame,
                values=self.recent_files,
                state="readonly",
                width=60
            )
            recent_combo.pack(side=tk.LEFT, padx=5)
            recent_combo.bind("<<ComboboxSelected>>",
                              lambda e: self.input_path.set(recent_combo.get()))

        # Output directory section
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="5")
        output_frame.pack(fill=tk.X, pady=5)

        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        output_btn = ttk.Button(
            output_frame,
            text="Browse...",
            command=self._browse_output
        )
        output_btn.pack(side=tk.LEFT)

        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.pack(fill=tk.X, pady=5)

        ttk.Label(options_frame, text="Documentation Title:").pack(side=tk.LEFT)
        title_entry = ttk.Entry(options_frame, textvariable=self.title, width=40)
        title_entry.pack(side=tk.LEFT, padx=5)

        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress,
            maximum=100,
            mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X)

        status_label = ttk.Label(progress_frame, textvariable=self.status)
        status_label.pack(pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.generate_btn = ttk.Button(
            button_frame,
            text="Generate Documentation",
            command=self._generate
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        self.open_btn = ttk.Button(
            button_frame,
            text="Open Output",
            command=self._open_output,
            state=tk.DISABLED
        )
        self.open_btn.pack(side=tk.LEFT, padx=5)

        quit_btn = ttk.Button(
            button_frame,
            text="Quit",
            command=self.root.quit
        )
        quit_btn.pack(side=tk.RIGHT, padx=5)

        # Info
        info_label = ttk.Label(
            main_frame,
            text="Generates HTML documentation from Therefore configuration XML exports.",
            foreground="gray"
        )
        info_label.pack(side=tk.BOTTOM, pady=10)

    def _browse_input(self):
        """Browse for input file."""
        filename = filedialog.askopenfilename(
            title="Select Therefore Configuration File",
            filetypes=[
                ("XML files", "*.xml"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_path.set(filename)
            self._add_recent_file(filename)

    def _browse_output(self):
        """Browse for output directory."""
        dirname = filedialog.askdirectory(
            title="Select Output Directory"
        )
        if dirname:
            self.output_dir.set(dirname)

    def _generate(self):
        """Generate documentation in a background thread."""
        input_path = self.input_path.get()
        output_dir = self.output_dir.get()
        title = self.title.get()

        if not input_path:
            messagebox.showerror("Error", "Please select an input configuration file.")
            return

        if not Path(input_path).exists():
            messagebox.showerror("Error", f"Input file not found: {input_path}")
            return

        # Disable button during generation
        self.generate_btn.config(state=tk.DISABLED)
        self.open_btn.config(state=tk.DISABLED)
        self.progress.set(0)
        self.status.set("Processing...")

        # Run in background thread
        thread = threading.Thread(
            target=self._generate_thread,
            args=(input_path, output_dir, title),
            daemon=True
        )
        thread.start()

    def _generate_thread(self, input_path, output_dir, title):
        """Background thread for generation."""
        try:
            # Parse
            self._update_status("Parsing configuration...", 20)
            parser = ConfigurationParser()
            config = parser.parse(input_path)

            # Generate
            self._update_status("Generating documentation...", 60)
            output_file = Path(output_dir) / "documentation.html"
            generator = HTMLGenerator(config, title=title)
            output_path = generator.generate(str(output_file))

            # Done
            self._update_status(f"Complete! Output: {output_path}", 100)
            self._add_recent_file(input_path)

            # Enable open button
            self.root.after(0, lambda: self.open_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))

            # Store output path for open button
            self.output_path = output_path

        except Exception as e:
            self._update_status(f"Error: {str(e)}", 0)
            self.root.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def _update_status(self, message, progress):
        """Update status from background thread."""
        self.root.after(0, lambda: self.status.set(message))
        self.root.after(0, lambda: self.progress.set(progress))

    def _open_output(self):
        """Open the generated output file."""
        if hasattr(self, 'output_path') and Path(self.output_path).exists():
            webbrowser.open(f"file://{self.output_path}")
        else:
            messagebox.showinfo("Info", "Please generate documentation first.")

    def _load_recent_files(self):
        """Load recent files from config."""
        try:
            if self.config_file.exists():
                data = json.loads(self.config_file.read_text())
                self.recent_files = data.get("recent_files", [])[:10]
        except Exception:
            self.recent_files = []

    def _add_recent_file(self, filepath):
        """Add a file to recent files list."""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        self.recent_files.insert(0, filepath)
        self.recent_files = self.recent_files[:10]

        try:
            self.config_file.write_text(json.dumps({
                "recent_files": self.recent_files
            }))
        except Exception:
            pass

    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for GUI."""
    app = ConfigProcessorGUI()
    app.run()


if __name__ == "__main__":
    main()
