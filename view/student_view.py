import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv, os
import datetime

from model.student_model import StudentModel
from view.base_view import BaseView


class StudentView(BaseView):
    def __init__(self, parent, db, config_file="config.json"):
        super().__init__(parent)
        self.db = db
        self.model = StudentModel(db)
        self.load_config(config_file)
        self.apply_theme()
        
        # This will store the ID of the student being edited
        self.current_student_id = None

        self.create_header()
        self.create_theme_toggle()
        self.create_form()
        self.create_search()
        self.create_table()
        self.load_courses_dropdown()
        self.load_students()

    # ------------------------------
    # HEADER
    # ------------------------------
    def create_header(self):
        tk.Label(self, text="🎓 Student Management",
                 font=("Segoe UI", 20, "bold"),
                 bg=self.bg, fg="#5865F2").pack(pady=15)

    def create_theme_toggle(self):
        frame = tk.Frame(self, bg=self.bg)
        frame.pack(fill="x", padx=20, pady=5)
        self.theme_button = tk.Button(
            frame,
            text=f"Switch to {'Light' if self.theme=='dark' else 'Dark'} Mode",
            command=self.toggle_theme
        )
        self.theme_button.pack(side="right")

    # ------------------------------
    # STUDENT FORM
    # ------------------------------
    def create_form(self):
        self.form_frame = tk.LabelFrame(self, text="Student Details", padx=15, pady=15)
        self.form_frame.pack(fill="x", padx=20, pady=10)

        labels = ["Student no", "First Name", "Last Name", "Email", "Course"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.form_frame, text=label).grid(row=i, column=0, sticky="w", pady=5)
            if label == "Course":
                self.course_var = tk.StringVar()
                combo = ttk.Combobox(self.form_frame, textvariable=self.course_var, width=37, state="readonly")
                combo.grid(row=i, column=1, pady=5, padx=5)
                self.entries["course"] = combo
            else:
                entry = tk.Entry(self.form_frame, width=40)
                entry.grid(row=i, column=1, pady=5, padx=5)
                self.entries[label.lower().replace(" ", "_")] = entry

        # Buttons
        button_frame = tk.Frame(self.form_frame, bg=self.form_bg)
        button_frame.grid(row=0, column=2, rowspan=5, padx=20, sticky="n")

        self.btn_add = tk.Button(button_frame, text="Add", command=self.save_student)
        self.btn_update = tk.Button(button_frame, text="Update", command=self.update_student)
        self.btn_delete = tk.Button(button_frame, text="Delete", command=self.delete_student)
        self.btn_clear = tk.Button(button_frame, text="Clear Fields", command=self.clear_form)
        self.btn_export = tk.Button(button_frame, text="Export Logs", command=self.export_logs)
        self.btn_view_logs = tk.Button(button_frame, text="View Logs", command=self.view_logs)
        self.btn_audit = tk.Button(button_frame, text="View Audit Log", command=self.view_audit_log)
 

        for b in [self.btn_add, self.btn_update, self.btn_delete,
                  self.btn_clear, self.btn_export, self.btn_view_logs, self.btn_audit]:
            b.pack(pady=5)

    def clear_form(self):
        self.current_student_id = None
        for widget in self.entries.values():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
        
        # Reset button states
        self.btn_add.config(state="normal")
        self.btn_update.config(state="disabled")
        self.btn_delete.config(state="disabled")

    # ------------------------------
    # CRUD METHODS
    # ------------------------------
    def save_student(self):
        student_no = self.entries['student_no'].get().strip()
        first_name = self.entries['first_name'].get().strip()
        last_name = self.entries['last_name'].get().strip()
        email = self.entries['email'].get().strip()
        course_name = self.entries['course'].get().strip()

        if not (student_no and first_name and last_name and email and course_name):
            messagebox.showerror("Error", "All fields are required.")
            return

        course_row = self.db.fetchone("SELECT id FROM courses WHERE course_name = ?", (course_name,))
        if not course_row:
            messagebox.showerror("Error", "Selected course not found.")
            return
        course_id = course_row[0]

        try:
            self.model.add_student(student_no, first_name, last_name, email, course_id)
            messagebox.showinfo("Success", "Student added successfully.")
            self.load_students()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")
            
    def update_student(self):
        if self.current_student_id is None:
            messagebox.showwarning("Select Student", "Please select a student to update.")
            return
      
        student_no = self.entries['student_no'].get().strip()
        first_name = self.entries['first_name'].get().strip()
        last_name = self.entries['last_name'].get().strip()
        email = self.entries['email'].get().strip()
        course_name = self.entries['course'].get().strip()

        if not (student_no and first_name and last_name and email and course_name):
            messagebox.showerror("Error", "All fields are required.")
            return

        course_row = self.db.fetchone("SELECT id FROM courses WHERE course_name = ?", (course_name,))
        if not course_row:
            messagebox.showerror("Error", "Selected course not found.")
            return
        course_id = course_row[0]

        try:
            self.model.update_student(self.current_student_id, student_no, first_name, last_name, email, course_id)
            messagebox.showinfo("Success", "Student updated successfully.")
            self.load_students()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {e}")

    def delete_student(self):
        if self.current_student_id is None:
            messagebox.showwarning("Delete Student", "Please select a student to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?")
        if not confirm:
            return

        try:
            self.model.delete_student(self.current_student_id)
            messagebox.showinfo("Deleted", "Student deleted successfully.")
            self.load_students()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete student: {e}")

    def load_students(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.model.get_all_students()
        for r in rows:
            self.tree.insert("", "end", values=(r["id"], r["student_no"], r["name"], r["email"], r["course"]))

    def search_student(self):
        term = self.search_var.get().strip()
        rows = self.model.search_students(term)
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=(r["id"], r["student_no"], r["name"], r["email"], r["course"]))

    # ------------------------------
    # COURSE DROPDOWN
    # ------------------------------
    def load_courses_dropdown(self):
        rows = self.db.fetchall("SELECT course_name FROM courses ORDER BY course_name")
        course_names = [r[0] for r in rows]
        self.entries["course"]["values"] = course_names

    # ------------------------------
    # SEARCH BAR + TABLE
    # ------------------------------
    def create_search(self):
        frame = tk.Frame(self, bg=self.bg)
        frame.pack(fill="x", padx=20, pady=10)

        tk.Label(frame, text="🔎 Search:").pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.search_var, width=40).pack(side="left", padx=10)
        tk.Button(frame, text="Search", command=self.search_student,
                  bg=self.button_bg, fg=self.button_fg).pack(side="left", padx=5)
        tk.Button(frame, text="Clear", command=self.load_students,
                  bg=self.button_bg, fg=self.button_fg).pack(side="left", padx=5)

    def create_table(self):
        frame = tk.Frame(self, bg=self.bg)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("ID", "Student No", "Firstname Lastname", "Email", "Course")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            self.clear_form()
            return
        
        values = self.tree.item(selected[0])["values"]
        if len(values) < 4:
            return

        self.current_student_id = values[0]
        
        # Split full name into first/last
        full_name = values[2]
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        self.entries["student_no"].delete(0, tk.END)
        self.entries["student_no"].insert(0, values[1])
        self.entries["first_name"].delete(0, tk.END)
        self.entries["first_name"].insert(0, first_name)
        self.entries["last_name"].delete(0, tk.END)
        self.entries["last_name"].insert(0, last_name)
        self.entries["email"].delete(0, tk.END)
        self.entries["email"].insert(0, values[3])
        self.entries["course"].set(values[4])
        
        self.btn_add.config(state="disabled")
        self.btn_update.config(state="normal")
        self.btn_delete.config(state="normal")

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
            rows = self.model.get_all_students()
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")
                writer.writerow(["Exported", timestamp])  # Add timestamp row
                writer.writerow(["ID", "Student No", "Firstname Lastname", "Email", "Course"])
                for r in rows:
                    writer.writerow([r["id"], r["student_no"], r["name"], r["email"], r["course"]])
            messagebox.showinfo("Export Logs", f"Logs exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs: {e}")

    def view_logs(self):
        try:
            rows = self.model.get_all_students()
            if not rows:
                messagebox.showinfo("View Logs", "No student records found.")
                return
            log_window = tk.Toplevel(self)
            log_window.title("Student Logs")
            log_window.geometry("600x400")
            cols = ("ID", "Student No", "Name", "Email", "Course")
            tree = ttk.Treeview(log_window, columns=cols, show="headings")
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor="center")
            tree.pack(fill="both", expand=True)
            for r in rows:
                tree.insert("", "end", values=(r["id"], r["student_no"], r["name"], r["email"], r["course"]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load logs: {e}")

    def view_audit_log(self):
        log_path = "logs/student_audit.log"
        if not os.path.exists(log_path):
            messagebox.showinfo("Audit Log", "No audit log file found.")
            return

        log_window = tk.Toplevel(self)
        log_window.title("Student Audit Log")
        log_window.geometry("800x500")

        text = tk.Text(log_window, wrap="none", font=("Consolas", 10))
        text.pack(fill="both", expand=True)

        with open(log_path, "r", encoding="utf-8") as f:
            log_content = f.read()
            text.insert("1.0", log_content)
        text.config(state="disabled")

        # Optional: Add a vertical scrollbar
        scrollbar = ttk.Scrollbar(log_window, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")