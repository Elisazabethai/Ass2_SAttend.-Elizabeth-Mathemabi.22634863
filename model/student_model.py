import os
import datetime

class StudentModel:
    def __init__(self, db):
        self.db = db
        self.create_table()
        self.log_file = os.path.join("logs", "student_audit.log")
        os.makedirs("logs", exist_ok=True)

    def log_action(self, action, student_data):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | {action} | {student_data}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def create_table(self):
        """Create students table if it does not exist"""
        query = """
        CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_no TEXT UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                course_id INTEGER,
                FOREIGN KEY(course_id) REFERENCES courses(id)
        )
        """
        self.db.execute(query)

    # ------------------------------
    # CRUD OPERATIONS
    # ------------------------------
    def add_student(self, student_no, first_name, last_name, email, course_id):
        query = "INSERT INTO students (student_no, first_name, last_name, email, course_id) VALUES (?, ?, ?, ?, ?)"
        self.db.execute(query, (student_no, first_name, last_name, email, course_id))
        self.log_action("ADD", {
            "student_no": student_no,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "course_id": course_id
        })

    def update_student(self, id, student_no, first_name, last_name, email, course_id):
        query = """
        UPDATE students
        SET student_no = ?, first_name = ?, last_name = ?, email = ?, course_id = ?
        WHERE id = ?
        """
        self.db.execute(query, (student_no, first_name, last_name, email, course_id, id))
        self.log_action("UPDATE", {
            "id": id,
            "student_no": student_no,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "course_id": course_id
        })

    def delete_student(self, student_id):
        # Fetch student details before deletion for logging
        row = self.db.fetchone("SELECT student_no, first_name, last_name, email, course_id FROM students WHERE id = ?", (student_id,))
        query = "DELETE FROM students WHERE id = ?"
        self.db.execute(query, (student_id,))
        if row:
            self.log_action("DELETE", {
                "id": student_id,
                "student_no": row["student_no"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "course_id": row["course_id"]
            })

    def get_all_students(self):
        query = """
        SELECT s.id, s.student_no, s.first_name, s.last_name, s.email, s.course_id, c.course_name
        FROM students s
        LEFT JOIN courses c ON s.course_id = c.id
        """
        rows = self.db.fetchall(query)
        # Create a single 'name' field for the view
        return [
            {
            "id": r["id"],
            "student_no": r["student_no"],
            "name": f"{r['first_name']} {r['last_name']}",
            "email": r["email"],
            "course": r["course_name"]

            }
            for r in rows
        ]

    def search_students(self, term):
        query = """
        SELECT s.id, s.student_no, s.first_name, s.last_name, s.email, c.course_name
        FROM students s
        LEFT JOIN courses c ON s.course_id = c.id
        WHERE s.student_no LIKE ? OR s.first_name LIKE ? OR s.last_name LIKE ? OR s.email LIKE ?
        """
        term_like = f"%{term}%"
        rows = self.db.fetchall(query, (term_like, term_like, term_like, term_like))
        # Combine first and last name for the 'name' field in the view
        return [
            {"id": r[0], "student_no": f"{r[1]}", "name": f"{r[2]} {r[3]}", "email": r[4], "course": r[5]}
            for r in rows
        ]
    
    def get_course_name(self, course_id):
        row = self.db.fetchone("SELECT course_name FROM courses WHERE id = ?", (course_id,))
        return row["course_name"] if row else ""