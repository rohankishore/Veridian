import os

# Path to the database
with open("resources/data/current_db.txt") as db_file:
    db_path = db_file.read()
DB_PATH = db_path


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
            is_complete INTEGER DEFAULT 0, -- Add the is_complete column
            FOREIGN KEY (subject_id) REFERENCES Subjects (id) ON DELETE CASCADE
        )
    """)

    # Check if `is_complete` column exists and add it if necessary
    cursor.execute("PRAGMA table_info(Chapters)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'is_complete' not in columns:
        cursor.execute("ALTER TABLE Chapters ADD COLUMN is_complete INTEGER DEFAULT 0")
        print("Added 'is_complete' column to Chapters table.")

    conn.commit()
    conn.close()

def add_chapter_to_db(subject_id, chapter_name):
    """Insert a new chapter into the database."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO chapters (subject_id, name, is_complete)
        VALUES (?, ?, 0)  -- Default 'is_complete' to 0 (incomplete)
    """, (subject_id, chapter_name))
    connection.commit()
    connection.close()


def delete_chapter_from_db(chapter_id):
    """Delete a chapter from the database."""
    try:
        connection = sqlite3.connect(DB_PATH)  # Replace with your database name
        cursor = connection.cursor()

        # SQL query to delete the chapter
        cursor.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))

        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error deleting chapter: {e}")

import sqlite3

def fetch_chapters(subject_id):
    """Fetch all chapters for a given subject."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, name, is_complete FROM chapters WHERE subject_id = ?
    """, (subject_id,))
    chapters = cursor.fetchall()
    connection.close()
    return chapters

def add_chapter_to_db(subject_id, name):
    """Add a chapter to the database."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO chapters (subject_id, name) VALUES (?, ?)
    """, (subject_id, name))
    connection.commit()
    connection.close()

def update_chapter_completion(chapter_id, is_complete):
    """Toggle completion status of a chapter."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE chapters SET is_complete = ? WHERE id = ?
    """, (1 if is_complete else 0, chapter_id))
    connection.commit()
    connection.close()

def fetch_subtopics(chapter_id):
    """Fetch all subtopics for a given chapter."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, name, is_complete FROM subtopics WHERE chapter_id = ?
    """, (chapter_id,))
    subtopics = cursor.fetchall()
    connection.close()
    return subtopics

def add_subtopic_to_db(chapter_id, name):
    """Add a subtopic to the database."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO subtopics (chapter_id, name) VALUES (?, ?)
    """, (chapter_id, name))
    connection.commit()
    connection.close()

def update_subtopic_completion(subtopic_id, is_complete):
    """Toggle completion status of a subtopic."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE subtopics SET is_complete = ? WHERE id = ?
    """, (1 if is_complete else 0, subtopic_id))
    connection.commit()
    connection.close()


def calculate_subject_completion(subject_id):
    """Calculate the percentage of completed chapters in a subject."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM chapters WHERE subject_id = ?", (subject_id,))
    total_chapters = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM chapters WHERE subject_id = ? AND completed = 1", (subject_id,))
    completed_chapters = cursor.fetchone()[0]

    connection.close()
    return int((completed_chapters / total_chapters) * 100) if total_chapters > 0 else 0

def update_chapter_completion(chapter_id, is_complete):
    """Update the completion status of a chapter in the database."""
    query = "UPDATE chapters SET is_complete = ? WHERE id = ?"
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(query, (is_complete, chapter_id))
    connection.commit()


def calculate_project_completion(project_id):
    """Calculate the percentage of completed subjects in a project."""
    connection = sqlite3.connect(DB_PATH)
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
    """Fetch chapters for the given subject."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, is_complete FROM chapters WHERE subject_id = ?", (subject_id,))
    chapters = cursor.fetchall()
    conn.close()
    return chapters

def mark_chapter_complete(chapter_id, is_complete):
    """Mark a chapter as complete or incomplete."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE chapters SET is_complete = ? WHERE id = ?", (1 if is_complete else 0, chapter_id))
    conn.commit()
    conn.close()

def calculate_subject_completion(subject_id):
    """Calculate the completion percentage of a subject based on its chapters."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chapters WHERE subject_id = ? AND is_complete = 1", (subject_id,))
    completed_chapters = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM chapters WHERE subject_id = ?", (subject_id,))
    total_chapters = cursor.fetchone()[0]
    conn.close()

    if total_chapters == 0:
        return 0  # Prevent division by zero

    return (completed_chapters / total_chapters) * 100

def delete_project(project_id):
    """Delete a project and its associated subjects and chapters from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Delete all related chapters first
    cursor.execute("DELETE FROM chapters WHERE subject_id IN (SELECT id FROM subjects WHERE project_id = ?)",
                   (project_id,))
    # Delete all related subjects
    cursor.execute("DELETE FROM subjects WHERE project_id = ?", (project_id,))
    # Delete the project itself
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()


# Initialize the database when the script is run
initialize_db()
