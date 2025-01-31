import os
import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPalette, QBrush, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidgetItem, QHBoxLayout, QMenu, QMessageBox, QDialog
from qfluentwidgets import (ListWidget, LineEdit, PushButton, MessageBox)

from study_db_helpers import add_project, fetch_projects, delete_project#, fetch_project_completion


def check_curr_db():
    try:
        with open("resources/data/current_db.txt", "r+") as db_file:
            path = db_file.read()
            db_file.close()
            return path
    except Exception as e:
        print(f"Error reading curr db:-  {e}")


def create_new_default_project():
    # Logic to create a fresh default project in the study_projects.db
    add_project(db_path="resources/data/study_projects.db", project_name="New Default Project")


from shutil import copyfile


def migrate_tables(source_db, target_db):
    try:
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)

        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()

        # Fetch all tables from the source database
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = source_cursor.fetchall()

        for table in tables:
            table_name = table[0]

            # Check if the table already exists in the target database
            target_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            if target_cursor.fetchone():
                print(f"Skipping existing table: {table_name}")
                continue  # Skip migration if the table already exists

            # Copy the table structure
            source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            create_table_sql = source_cursor.fetchone()[0]
            target_cursor.execute(create_table_sql)

            # Copy the data
            source_cursor.execute(f"SELECT * FROM {table_name};")
            rows = source_cursor.fetchall()

            if rows:
                placeholders = ', '.join(['?' for _ in rows[0]])
                target_cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders});", rows)

        target_conn.commit()
        print("Tables migrated successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        source_conn.close()
        target_conn.close()

def migrate_data(source_db, target_db):
    try:
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)

        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()

        # Attach source database to target
        target_cursor.execute(f"ATTACH DATABASE '{source_db}' AS src_db")

        # Get table names
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = source_cursor.fetchall()

        for table in tables:
            table_name = table[0]

            if table_name == "sqlite_sequence":
                print("Skipping migration of sqlite_sequence table.")
                continue

            print(f"Migrating table: {table_name}")

            # Check if the table exists in the target database
            target_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not target_cursor.fetchone():
                print(f"Creating table: {table_name}")
                source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                create_table_sql = source_cursor.fetchone()[0]
                target_cursor.execute(create_table_sql)

            # Insert the data
            source_cursor.execute(f"SELECT * FROM {table_name}")
            rows = source_cursor.fetchall()
            if rows:
                placeholders = ', '.join(['?' for _ in rows[0]])
                target_cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)
                print(f"Data for {table_name} migrated successfully!")

        target_conn.commit()

    except Exception as e:
        print(f"Error during migration: {e}")

    finally:
        source_conn.close()
        target_conn.close()

def fetch_project_completion(project_id):
    try:
        conn = sqlite3.connect("resources/data/study_projects.db")
        cursor = conn.cursor()
        cursor.execute("SELECT completion FROM projects WHERE project_id=?", (project_id,))
        completion = cursor.fetchone()
        conn.close()
        return completion[0] if completion else 0  # Ensure it returns 0 if no completion is found
    except Exception as e:
        print(f"Error fetching completion: {e}")
        return 0  # Default value if there's an issue

def update_project_completion(project_id, completion_value):
    try:
        conn = sqlite3.connect("resources/data/study_projects.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET completion=? WHERE project_id=?", (completion_value, project_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating completion: {e}")

class CardButtonDialog(QDialog):
    def __init__(self, image_path: None, button_text: None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Templates")
        self.setFixedSize(500, 300)
        self.setStyleSheet("""
                    QDialog {
                        background: qlineargradient(
                            spread:pad, x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #202020, stop:1 #202020
                        );
                        border-radius: 10px;
                    }
                """)

        # Set up the layout
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.jee_button = PushButton()
        self.jee_button.setFixedSize(200, 250)
        self.jee_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #ddd;
                border-radius: 15px;
                background-color: #EEEEEE;
            }
            QPushButton:hover {
                background-color: #d2d2d2;
            }
            QPushButton:pressed {
                background-color: #d9d9d9;
            }
        """)

        if check_curr_db() == "resources/data/jee.db":
            self.jee_button.setDisabled(True)

        self.default_button = PushButton()
        self.default_button.setFixedSize(200, 250)
        self.default_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #ddd;
                border-radius: 15px;
                background-color: #EEEEEE;
            }
            QPushButton:hover {
                background-color: #d2d2d2;
            }
            QPushButton:pressed {
                background-color: #d9d9d9;
            }
        """)

        if check_curr_db() == "resources/data/study_projects.db":
            self.default_button.setDisabled(True)

        # Add the image to the button
        jee_pixmap = QPixmap("resources/icons/NTA.png")
        jee_pixmap_label = QLabel()
        jee_pixmap_label.setPixmap(jee_pixmap.scaled(180, 140, Qt.AspectRatioMode.KeepAspectRatio))
        jee_pixmap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add text below the image
        jee_text_label = QLabel("JEE Main")
        jee_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        jee_text_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        # Stack the image and text on the button
        jee_button_layout = QVBoxLayout(self.jee_button)
        jee_button_layout.setContentsMargins(5, 5, 5, 5)
        jee_button_layout.addWidget(jee_pixmap_label)
        jee_button_layout.addWidget(jee_text_label)

        def_pixmap = QPixmap("resources/icons/default.png")
        def_pixmap_label = QLabel()
        def_pixmap_label.setPixmap(def_pixmap.scaled(180, 140, Qt.AspectRatioMode.KeepAspectRatio))
        def_pixmap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add text below the image
        def_text_label = QLabel("Default")
        def_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        def_text_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        # Stack the image and text on the button
        def_button_layout = QVBoxLayout(self.default_button)
        def_button_layout.setContentsMargins(5, 5, 5, 5)
        def_button_layout.addWidget(def_pixmap_label)
        def_button_layout.addWidget(def_text_label)

        # Add the button to the dialog layout
        layout.addWidget(self.jee_button)

        # Connect button click to a custom method
        self.jee_button.clicked.connect(self.on_jee_button_clicked)

    def on_jee_button_clicked(self):
        jee_db = "resources/data/jee.db"
        current_db = check_curr_db()  # Get the current active database path
        current_db = os.path.normpath(current_db)  # Normalize path

        if current_db != jee_db:
            try:
                migrate_data(jee_db, current_db)  # Migrate tables without modifying current_db.txt
                print("Data migrated from JEE database to current database.")
            except Exception as e:
                print(f"Error migrating data: {e}")


def check_curr_db():
    try:
        with open("resources/data/current_db.txt", "r+") as db_file:
            path = db_file.read()
            return path
    except Exception as e:
        print(f"Error reading curr db:-  {e}")


class ProjectsWidget(QWidget):
    def __init__(self, switch_to_subjects_callback, back_to_main_callback=None):
        super().__init__()
        self.switch_to_subjects_callback = switch_to_subjects_callback
        self.back_to_main_callback = back_to_main_callback

        self.setStyleSheet("""
            background-color: #202020;
            color: white;
        """)

        self.layout = QVBoxLayout(self)

        self.title_label = QLabel("Projects")
        self.title_label.setFont(QFont("Poppins", 36, QFont.Weight.DemiBold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.title_label)

        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#202020"))
        gradient.setColorAt(1.0, QColor("#202020"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.input_layout = QHBoxLayout()
        self.project_input = LineEdit()
        self.project_input.setPlaceholderText("Enter a project name...")
        self.input_layout.addWidget(self.project_input)

        self.add_button = PushButton("Add Project")
        self.add_button.clicked.connect(self.add_project)
        self.input_layout.addWidget(self.add_button)

        self.template_button = PushButton("Templates")
        self.template_button.clicked.connect(self.template_card)
        self.input_layout.addWidget(self.template_button)

        self.layout.addLayout(self.input_layout)

        self.projects_list = ListWidget()
        self.projects_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.projects_list.customContextMenuRequested.connect(self.open_context_menu)
        self.projects_list.itemClicked.connect(self.open_project)
        self.layout.addWidget(self.projects_list)

        if self.back_to_main_callback:
            self.back_button = PushButton("Back to Main")
            self.back_button.setStyleSheet("""
                QPushButton {
                    background-color: #68E95C;
                    color: #ffffff;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #51b547;
                }
            """)
            self.back_button.clicked.connect(self.back_to_main_callback)
            self.layout.addWidget(self.back_button)

        self.load_projects()

    def refresh_projects(self):
        self.load_projects()

    def template_card(self):
        temp_dialog = CardButtonDialog(image_path="resources/icons/NTA.png", button_text="JEE")
        temp_dialog.exec()

    def load_projects(self):
        self.projects_list.clear()
        current_db = check_curr_db()  # Get the active DB path
        projects = fetch_projects(current_db)  # Fetch all projects

        for project_id, project_name in projects:
            completion = fetch_project_completion(project_id)
            item = QListWidgetItem(f"{project_name} ({completion}%)")
            item.setData(Qt.ItemDataRole.UserRole, project_id)
            self.projects_list.addItem(item)

    def add_project(self):
        project_name = self.project_input.text().strip()
        if project_name:
            current_db = check_curr_db()  # Get the current active database
            add_project(current_db, project_name)  # Pass the database path
            self.load_projects()
            self.project_input.clear()

    def open_project(self, item):
        project_id = item.data(Qt.ItemDataRole.UserRole)
        self.switch_to_subjects_callback(project_id)

    def open_context_menu(self, position):
        item = self.projects_list.itemAt(position)
        if item:
            project_id = item.data(Qt.ItemDataRole.UserRole)
            menu = QMenu(self)

            remove_action = menu.addAction("Remove Project")
            remove_action.triggered.connect(lambda: self.remove_project(project_id))

            menu.exec(self.projects_list.mapToGlobal(position))

    def remove_project(self, project_id):
        confirm_deletion = QMessageBox.question(
            self,
            "Confirm Project Deletion",
            "Are you sure you want to delete this project ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm_deletion == QMessageBox.StandardButton.Yes:
            delete_project(project_id)
            self.load_projects()
