import sqlite3
import os  # This line is kept for consistency, but can be removed if truly unused.

#  DB_FILE = "database.db"

DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "database.db")
print (f"Database file path: {DB_FILE}")


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT UNIQUE,
                course_name TEXT,
                lecturer TEXT,
                credits INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_no TEXT UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                course_id INTEGER,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        """)
        self.conn.commit()

    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetchone(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def close(self):
        # Close the DB connection
        self.conn.close()



