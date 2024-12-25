import sqlite3
import os

# Path to the database
DB_PATH = "resources/data/tasks.db"


def initialize_db():
    """Initialize the database and create tables if they don't exist."""
    if not os.path.exists("resources/data"):
        os.makedirs("resources/data")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Create Subjects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            FOREIGN KEY (project_id) REFERENCES Projects (id) ON DELETE CASCADE
        )
    """)

    # Create Chapters table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject_id INTEGER NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES Subjects (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def mark_chapter_complete(chapter_id):
    """Mark a chapter as complete."""
    connection = sqlite3.connect("resources/data/tasks.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE chapters SET completed = 1 WHERE id = ?", (chapter_id,))
    connection.commit()
    connection.close()


def calculate_subject_completion(subject_id):
    """Calculate the percentage of completed chapters in a subject."""
    connection = sqlite3.connect("resources/data/tasks.db")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM chapters WHERE subject_id = ?", (subject_id,))
    total_chapters = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM chapters WHERE subject_id = ? AND completed = 1", (subject_id,))
    completed_chapters = cursor.fetchone()[0]

    connection.close()
    return int((completed_chapters / total_chapters) * 100) if total_chapters > 0 else 0


def calculate_project_completion(project_id):
    """Calculate the percentage of completed subjects in a project."""
    connection = sqlite3.connect("resources/data/tasks.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM subjects WHERE project_id = ?", (project_id,))
    subject_ids = [row[0] for row in cursor.fetchall()]

    total_subjects = len(subject_ids)
    completed_subjects = sum(1 for subject_id in subject_ids if calculate_subject_completion(subject_id) == 100)

    connection.close()
    return int((completed_subjects / total_subjects) * 100) if total_subjects > 0 else 0


def add_project(name):
    """Add a new project to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO Projects (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Project '{name}' already exists.")
    finally:
        conn.close()


def fetch_projects():
    """Fetch all projects from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM Projects ORDER BY id")
    projects = cursor.fetchall()

    conn.close()
    return projects


def add_subject(project_id, name):
    """Add a new subject to a specific project."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Subjects (name, project_id) VALUES (?, ?)", (name, project_id))
    conn.commit()
    conn.close()


def fetch_subjects(project_id):
    """Fetch all subjects for a specific project."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM Subjects WHERE project_id = ? ORDER BY id", (project_id,))
    subjects = cursor.fetchall()

    conn.close()
    return subjects


def add_chapter(subject_id, name):
    """Add a new chapter to a specific subject."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Chapters (name, subject_id) VALUES (?, ?)", (name, subject_id))
    conn.commit()
    conn.close()


def fetch_chapters(subject_id):
    """Fetch all chapters for a specific subject."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM Chapters WHERE subject_id = ? ORDER BY id", (subject_id,))
    chapters = cursor.fetchall()

    conn.close()
    return chapters


# Initialize the database when the script is run
initialize_db()
