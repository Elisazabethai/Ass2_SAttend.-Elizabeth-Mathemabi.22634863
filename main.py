import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db import Database
import os
import json

from view.student_view import StudentView
from view.course_view import CourseView

CONFIG_FILE = "config.json"
#DB_FILE = "database.db"


# ------------------------------
# APPLICATION
# ------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student & Course Management System")
        self.geometry("1150x750")

        self.db = Database()
        self.load_config()
        
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.student_tab = StudentView(self.notebook, self.db, CONFIG_FILE)
        self.course_tab = CourseView(self.notebook, self.db, CONFIG_FILE)

        self.notebook.add(self.student_tab, text="Students")
        self.notebook.add(self.course_tab, text="Courses")

        # Sync theme toggle buttons
        self.sync_theme_buttons()

    # ------------------------------
    # CONFIG
    # ------------------------------
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {"theme": "light"}

    # ------------------------------
    # THEME SYNC
    # ------------------------------
    def sync_theme_buttons(self):
        def theme_callback():
            self.student_tab.toggle_theme()
            self.course_tab.toggle_theme()

        # Replace both buttons commands
        self.student_tab.theme_button.config(command=theme_callback)
        self.course_tab.theme_button.config(command=theme_callback)


# ------------------------------
# RUN APP
# ------------------------------
if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    app = App()
    app.mainloop()
