import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

from model.course_model import CourseModel
from view.base_view import BaseView


class CourseView(BaseView):
    def __init__(self, parent, db, config_file="config.json"):
        super().__init__(parent)
        self.db = db
        self.model = CourseModel(db)
        self.load_config(config_file)
        self.apply_theme()

        self.create_header()
        self.create_theme_toggle()
        self.create_form()
        self.create_search()
        self.create_table()
        self.load_courses()

    # ------------------------------
    # HEADER
    # ------------------------------
    def create_header(self):
        tk.Label(self, text="📚 Course Management",
                 font=("Segoe UI", 20, "bold"),
                 bg=self.bg, fg="#5865F2").pack(pady=15)

    def create_theme_toggle(self):
        frame = tk.Frame(self, bg=self.bg)
        frame.pack(fill="x", padx=20, pady=5)
        self.theme_button = tk.Button(
            frame,
            text=f"Switch to {'Dark' if self.theme=='light' else 'Light'} Mode",
            command=self.toggle_theme
        )
        self.theme_button.pack(side="right")

    # ------------------------------
    # COURSE FORM
    # ------------------------------
    def create_form(self):
        self.form_frame = tk.LabelFrame(self, text="Course Details", padx=15, pady=15)
        self.form_frame.pack(fill="x", padx=20, pady=10)

        labels = ["Course Code", "Course Name", "Lecturer", "Credits"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.form_frame, text=label).grid(row=i, column=0, sticky="w", pady=5)
            entry = tk.Entry(self.form_frame, width=40)
            entry.grid(row=i, column=1, pady=5, padx=5)
            self.entries[label.lower().replace(" ", "_")] = entry

        # Buttons
        button_frame = tk.Frame(self.form_frame, bg=self.form_bg)
        button_frame.grid(row=0, column=2, rowspan=5, padx=20, sticky="n")

        self.btn_add = tk.Button(button_frame, text="Add", command=self.save_course)
        self.btn_update = tk.Button(button_frame, text="Update", command=self.update_course)
        self.btn_delete = tk.Button(button_frame, text="Delete", command=self.delete_course)
        self.btn_clear = tk.Button(button_frame, text="Clear", command=self.clear_form)
        self.btn_export = tk.Button(button_frame, text="Export Logs", command=self.export_logs)
        self.btn_view_logs = tk.Button(button_frame, text="View Logs", command=self.view_logs)

        for b in [self.btn_add, self.btn_update, self.btn_delete,
                  self.btn_clear, self.btn_export, self.btn_view_logs]:
            b.pack(pady=5)

    def clear_form(self):
        for widget in self.entries.values():
            widget.delete(0, tk.END)

    # ------------------------------
    # CRUD METHODS
    # ------------------------------
    def save_course(self):
        code = self.entries['course_code'].get().strip()
        name = self.entries['course_name'].get().strip()
        lecturer = self.entries['lecturer'].get().strip()
        credits = self.entries['credits'].get().strip()
        if not (code and name and lecturer and credits):
            messagebox.showerror("Error", "All fields are required.")
            return
        try:
            self.model.add_course(code, name, lecturer, credits)
            messagebox.showinfo("Success", "Course added successfully.")
            self.load_courses()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add course: {e}")

    def update_course(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Course", "Please select a course to update.")
            return
        id = self.tree.item(selected[0])["values"][0]
        try:
            self.model.update_course(
                id,
                self.entries['course_code'].get().strip(),
                self.entries['course_name'].get().strip(),
                self.entries['lecturer'].get().strip(),
                self.entries['credits'].get().strip()
            )
            messagebox.showinfo("Success", "Course updated successfully.")
            self.load_courses()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update course: {e}")

    def delete_course(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Delete Course", "Please select a course to delete.")
            return
        id = self.tree.item(selected[0])["values"][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this course?")
        if not confirm:
            return
        try:
            self.model.delete_course(id)
            messagebox.showinfo("Deleted", "Course deleted successfully.")
            self.load_courses()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete course: {e}")

    def load_courses(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.model.get_all_courses()
        for r in rows:
            self.tree.insert("", "end", values=(r["id"], r["course_code"], r["course_name"], r["lecturer"], r["credits"]))

    def search_course(self):
        term = self.search_var.get().strip()
        rows = self.model.search_courses(term)
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=(r["id"], r["course_code"], r["course_name"], r["lecturer"], r["credits"]))

    # ------------------------------
    # SEARCH BAR + TABLE
    # ------------------------------
    def create_search(self):
        frame = tk.Frame(self, bg=self.bg)
        frame.pack(fill="x", padx=20, pady=10)

        tk.Label(frame, text="🔎 Search:").pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.search_var, width=40).pack(side="left", padx=10)
        tk.Button(frame, text="Search", command=self.search_course,
                  bg=self.button_bg, fg=self.button_fg).pack(side="left", padx=5)
        tk.Button(frame, text="Clear", command=self.load_courses,
                  bg=self.button_bg, fg=self.button_fg).pack(side="left", padx=5)

    def create_table(self):
        frame = tk.Frame(self, bg=self.bg)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("ID", "Course Code", "Course Name", "Lecturer", "Credits")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        if len(values) < 5:
            return
        self.entries['course_code'].delete(0, tk.END)
        self.entries['course_code'].insert(0, values[1])
        self.entries['course_name'].delete(0, tk.END)
        self.entries['course_name'].insert(0, values[2])
        self.entries['lecturer'].delete(0, tk.END)
        self.entries['lecturer'].insert(0, values[3])
        self.entries['credits'].delete(0, tk.END)
        self.entries['credits'].insert(0, values[4])

    # ------------------------------
    # LOGS
    # ------------------------------
    def export_logs(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if not file_path:
                return
            rows = self.model.get_all_courses()
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Course Code", "Course Name", "Lecturer", "Credits"])
                for r in rows:
                    writer.writerow([r["id"], r["course_code"], r["course_name"], r["lecturer"], r["credits"]])
            messagebox.showinfo("Export Logs", f"Logs exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs: {e}")

    def view_logs(self):
        try:
            rows = self.model.get_all_courses()
            if not rows:
                messagebox.showinfo("View Logs", "No course records found.")
                return
            log_window = tk.Toplevel(self)
            log_window.title("Course Logs")
            log_window.geometry("600x400")
            cols = ("ID", "Course Code", "Course Name", "Lecturer", "Credits")
            tree = ttk.Treeview(log_window, columns=cols, show="headings")
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor="center")
            tree.pack(fill="both", expand=True)
            for r in rows:
                tree.insert("", "end", values=(r["id"], r["course_code"], r["course_name"], r["lecturer"], r["credits"]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load logs: {e}")
