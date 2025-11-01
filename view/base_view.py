import tkinter as tk
from tkinter import ttk
import json

class BaseView(tk.Frame):
    def load_config(self, config_file):
        self.config_file = config_file
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {}
        self.theme = self.config.get("theme", "light")
        self.colors = self.config.get("colors", {})

    def apply_theme(self):
        c = self.colors[self.theme]
        self.bg = c["bg"]
        self.form_bg = c["form_bg"]
        self.button_bg = c["button_bg"]
        self.button_fg = c["button_fg"]
        self.entry_bg = c["entry_bg"]
        self.entry_fg = c["entry_fg"]
        self.tree_bg = c["tree_bg"]
        self.tree_fg = c["tree_fg"]
        self.configure(bg=self.bg)
        self.refresh_colors()

    def refresh_colors(self):
        for widget in self.winfo_children():
            self._apply_widget_colors(widget)

    def _apply_widget_colors(self, widget):
        if isinstance(widget, (tk.Frame, tk.LabelFrame)):
            widget.config(bg=self.form_bg if isinstance(widget, tk.LabelFrame) else self.bg)
        if isinstance(widget, tk.Label):
            widget.config(bg=self.form_bg if isinstance(widget.master, tk.LabelFrame) else self.bg,
                          fg=self.entry_fg, font=("Segoe UI", 10))
        if isinstance(widget, tk.Entry):
            widget.config(bg=self.entry_bg, fg=self.entry_fg, relief="flat", highlightthickness=1,
                          highlightbackground="#7289da")
        if isinstance(widget, ttk.Combobox):
            widget.config(background=self.entry_bg, foreground=self.entry_fg)
        if isinstance(widget, tk.Button):
            widget.config(bg=self.button_bg, fg=self.button_fg, relief="flat", padx=10, pady=5,
                          font=("Segoe UI", 10, "bold"))
            widget.bind("<Enter>", lambda e, b=widget: b.config(bg="#4752c4"))
            widget.bind("<Leave>", lambda e, b=widget: b.config(bg=self.button_bg))
        if isinstance(widget, ttk.Treeview):
            style = ttk.Style()
            style.configure("Treeview", background=self.tree_bg, foreground=self.tree_fg,
                            fieldbackground=self.tree_bg, rowheight=28, font=("Segoe UI", 10))
            style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        for child in widget.winfo_children():
            self._apply_widget_colors(child)
    def toggle_theme(self):
        # Toggle between 'light' and 'dark'
        self.theme = "dark" if self.theme == "light" else "light"
        # Save theme back to config.json
        self.config["theme"] = self.theme
        with open(self.config_file, "w", encoding="utf-8") as f:
            import json
            json.dump(self.config, f, indent=4)
        # Reapply colors
        self.apply_theme()
        # Update button text if it exists
        if hasattr(self, "theme_button"):
            self.theme_button.config(
                text=f"Switch to {'Light' if self.theme=='dark' else 'Dark'} Mode"
            )
