class CourseModel:
    def __init__(self, db):
        self.db = db
        self.create_table()

    def create_table(self):
        """Create courses table if it does not exist"""
        query = """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL UNIQUE,
            course_name TEXT NOT NULL,
            lecturer TEXT NOT NULL,
            credits INTEGER NOT NULL
        )
        """
        self.db.execute(query)

    # ------------------------------
    # CRUD OPERATIONS
    # ------------------------------
    def add_course(self, course_code, course_name, lecturer, credits):
        query = """
        INSERT INTO courses (course_code, course_name, lecturer, credits)
        VALUES (?, ?, ?, ?)
        """
        self.db.execute(query, (course_code, course_name, lecturer, credits))

    def update_course(self, course_id, course_code, course_name, lecturer, credits):
        query = """
        UPDATE courses
        SET course_code = ?, course_name = ?, lecturer = ?, credits = ?
        WHERE id = ?
        """
        self.db.execute(query, (course_code, course_name, lecturer, credits, course_id))

    def delete_course(self, course_id):
        query = "DELETE FROM courses WHERE id = ?"
        self.db.execute(query, (course_id,))

    def get_all_courses(self):
        query = "SELECT id, course_code, course_name, lecturer, credits FROM courses"
        rows = self.db.fetchall(query)
        return [
            {"id": r[0], "course_code": r[1], "course_name": r[2], "lecturer": r[3], "credits": r[4]}
            for r in rows
        ]

    def search_courses(self, term):
        query = """
        SELECT id, course_code, course_name, lecturer, credits
        FROM courses
        WHERE course_code LIKE ? OR course_name LIKE ? OR lecturer LIKE ?
        """
        term_like = f"%{term}%"
        rows = self.db.fetchall(query, (term_like, term_like, term_like))
        return [
            {"id": r[0], "course_code": r[1], "course_name": r[2], "lecturer": r[3], "credits": r[4]}
            for r in rows
        ]

    def get_course_by_id(self, course_id):
        query = "SELECT id, course_code, course_name, lecturer, credits FROM courses WHERE id = ?"
        row = self.db.fetchone(query, (course_id,))
        if row:
            return {"id": row[0], "course_code": row[1], "course_name": row[2], "lecturer": row[3], "credits": row[4]}
        return None
