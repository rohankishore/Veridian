import sqlite3


def initialize_study_db():
    connection = sqlite3.connect("study_projects.db")
    cursor = connection.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        )
    """)
    connection.commit()
    connection.close()


def add_project(name):
    connection = sqlite3.connect("study_projects.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
    connection.commit()
    connection.close()


def fetch_projects():
    connection = sqlite3.connect("study_projects.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, name FROM projects")
    projects = cursor.fetchall()
    connection.close()
    return projects


def add_subject(project_id, name):
    connection = sqlite3.connect("study_projects.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO subjects (project_id, name) VALUES (?, ?)", (project_id, name))
    connection.commit()
    connection.close()


def fetch_subjects(project_id):
    connection = sqlite3.connect("study_projects.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, name FROM subjects WHERE project_id = ?", (project_id,))
    subjects = cursor.fetchall()
    connection.close()
    return subjects


def add_chapter(subject_id, name):
    connection = sqlite3.connect("study_projects.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO chapters (subject_id, name) VALUES (?, ?)", (subject_id, name))
    connection.commit()
    connection.close()


def fetch_chapters(subject_id):
    connection = sqlite3.connect("study_projects.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, name FROM chapters WHERE subject_id = ?", (subject_id,))
    chapters = cursor.fetchall()
    connection.close()
    return chapters
