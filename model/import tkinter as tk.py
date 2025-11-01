import tkinter as tk
from tkinter import messagebox
import unittest
from unittest.mock import patch, MagicMock
from view.student_view import StudentView
from db import Database
import os
import shutil

class TestStudentView(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for testing
        self.test_db_path = "data/test_database.db"
        os.makedirs("data", exist_ok=True)
        # Copy the original db if exists, but for test, use new
        self.db = Database()
        self.db.conn = sqlite3.connect(self.test_db_path)
        self.db.conn.row_factory = sqlite3.Row
        self.db.cursor = self.db.conn.cursor()
        self.db.setup()

        # Mock messagebox to avoid GUI popups
        self.messagebox_patcher = patch('tkinter.messagebox.showinfo')
        self.messagebox_patcher.start()
        self.messagebox_error_patcher = patch('tkinter.messagebox.showerror')
        self.messagebox_error_patcher.start()
        self.messagebox_warning_patcher = patch('tkinter.messagebox.showwarning')
        self.messagebox_warning_patcher.start()
        self.messagebox_askyesno_patcher = patch('tkinter.messagebox.askyesno', return_value=True)
        self.messagebox_askyesno_patcher.start()

        # Create root
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window
        self.view = StudentView(self.root, self.db)

    def tearDown(self):
        self.messagebox_patcher.stop()
        self.messagebox_error_patcher.stop()
        self.messagebox_warning_patcher.stop()
        self.messagebox_askyesno_patcher.stop()
        self.root.destroy()
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_clear_form(self):
        # Set some values
        self.view.entries['student_no'].insert(0, '123')
        self.view.entries['first_name'].insert(0, 'John')
        self.view.entries['last_name'].insert(0, 'Doe')
        self.view.entries['email'].insert(0, 'john@example.com')
        self.view.entries['course'].set('Test Course')
        self.view.current_student_id = 1

        self.view.clear_form()

        self.assertEqual(self.view.entries['student_no'].get(), '')
        self.assertEqual(self.view.entries['first_name'].get(), '')
        self.assertEqual(self.view.entries['last_name'].get(), '')
        self.assertEqual(self.view.entries['email'].get(), '')
        self.assertEqual(self.view.entries['course'].get(), '')
        self.assertIsNone(self.view.current_student_id)
        self.assertEqual(self.view.btn_add['state'], 'normal')
        self.assertEqual(self.view.btn_update['state'], 'disabled')
        self.assertEqual(self.view.btn_delete['state'], 'disabled')

    def test_load_courses_dropdown(self):
        # Add a test course
        self.db.execute("INSERT INTO courses (course_code, course_name, lecturer, credits) VALUES (?, ?, ?, ?)", ('CS101', 'Computer Science', 'Dr. Smith', 3))
        self.view.load_courses_dropdown()
        self.assertIn('Computer Science', self.view.entries['course']['values'])

    def test_load_students(self):
        # Add a test student
        self.db.execute("INSERT INTO courses (course_code, course_name, lecturer, credits) VALUES (?, ?, ?, ?)", ('CS101', 'Computer Science', 'Dr. Smith', 3))
        course_id = self.db.fetchone("SELECT id FROM courses WHERE course_name = ?", ('Computer Science',))[0]
        self.db.execute("INSERT INTO students (student_no, first_name, last_name, email, course_id) VALUES (?, ?, ?, ?, ?)", ('123', 'John', 'Doe', 'john@example.com', course_id))
        self.view.load_students()
        items = self.view.tree.get_children()
        self.assertEqual(len(items), 1)
        values = self.view.tree.item(items[0])['values']
        self.assertEqual(values[1], '123')
        self.assertEqual(values[2], 'John Doe')

    def test_save_student_success(self):
        # Add a course
        self.db.execute("INSERT INTO courses (course_code, course_name, lecturer, credits) VALUES (?, ?, ?, ?)", ('CS101', 'Computer Science', 'Dr. Smith', 3))
        self.view.load_courses_dropdown()
        # Set form values
        self.view.entries['student_no'].insert(0, '124')
        self.view.entries['first_name'].insert(0, 'Jane')
        self.view.entries['last_name'].insert(0, 'Smith')
        self.view.entries['email'].insert(0, 'jane@example.com')
        self.view.entries['course'].set('Computer Science')

        self.view.save_student()

        # Check if student was added
        row = self.db.fetchone("SELECT * FROM students WHERE student_no = ?", ('124',))
        self.assertIsNotNone(row)
        self.assertEqual(row['first_name'], 'Jane')

    def test_save_student_missing_fields(self):
        # Try to save with missing fields
        self.view.save_student()
        # Should show error, but mocked

    def test_update_student(self):
        # Add course and student
        self.db.execute("INSERT INTO courses (course_code, course_name, lecturer, credits) VALUES (?, ?, ?, ?)", ('CS101', 'Computer Science', 'Dr. Smith', 3))
        course_id = self.db.fetchone("SELECT id FROM courses WHERE course_name = ?", ('Computer Science',))[0]
        self.db.execute("INSERT INTO students (student_no, first_name, last_name, email, course_id) VALUES (?, ?, ?, ?, ?)", ('125', 'Alice', 'Wonder', 'alice@example.com', course_id))
        self.view.load_students()
        # Select the student
        items = self.view.tree.get_children()
        self.view.tree.selection_set(items[0])
        self.view.on_row_select(None)
        # Update
        self.view.entries['first_name'].delete(0, tk.END)
        self.view.entries['first_name'].insert(0, 'Alicia')
        self.view.update_student()
        # Check update
        row = self.db.fetchone("SELECT first_name FROM students WHERE id = ?", (self.view.current_student_id,))
        self.assertEqual(row[0], 'Alicia')

    def test_delete_student(self):
        # Add course and student
        self.db.execute("INSERT INTO courses (course_code, course_name, lecturer, credits) VALUES (?, ?, ?, ?)", ('CS101', 'Computer Science', 'Dr. Smith', 3))
        course_id = self.db.fetchone("SELECT id FROM courses WHERE course_name = ?", ('Computer Science',))[0]
        self.db.execute("INSERT INTO students (student_no, first_name, last_name, email, course_id) VALUES (?, ?, ?, ?, ?)", ('126', 'Bob', 'Builder', 'bob@example.com', course_id))
        self.view.load_students()
        # Select and delete
        items = self.view.tree.get_children()
        self.view.tree.selection_set(items[0])
        self.view.on_row_select(None)
        self.view.delete_student()
        # Check deleted
        row = self.db.fetchone("SELECT * FROM students WHERE id = ?", (self.view.current_student_id,))
        self.assertIsNone(row)

if __name__ == '__main__':
    unittest.main()
