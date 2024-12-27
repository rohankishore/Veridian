from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPalette, QBrush, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidgetItem, QHBoxLayout, QMenu, QMessageBox, QDialog
from qfluentwidgets import (ListWidget, LineEdit, PushButton, MessageBox)

from study_db_helpers import add_project, fetch_projects, delete_project


def check_curr_db():
    try:
        with open("resources/data/current_db.txt", "r+") as db_file:
            path = db_file.read()
            db_file.close()
            return path
    except Exception as e:
        print(f"Error reading curr db:-  {e}")


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
        jee_text_label = QLabel("JEE")
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
        layout.addWidget(self.default_button)

        # Connect button click to a custom method
        self.jee_button.clicked.connect(self.on_jee_button_clicked)
        self.default_button.clicked.connect(self.on_default_button_clicked)

    def on_jee_button_clicked(self):
        try:
            with open("resources/data/current_db.txt", "r+") as db_file:
                db_file.truncate(0)
                db_file.write("resources/data/jee.db")
                db_file.close()
        except Exception as e:
            print(f"Error switching to JEE database: {e}")
        self.accept()

    def on_default_button_clicked(self):
        try:
            with open("resources/data/current_db.txt", "r+") as db_file:
                db_file.truncate(0)
                db_file.write("resources/data/study_projects.db")
                print("Switched to Default DB")
                db_file.close()
        except Exception as e:
            print(f"Error switching to Default database: {e}")
        self.accept()


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

        # Title
        self.title_label = QLabel("Projects")
        self.title_label.setFont(QFont("Poppins", 36, QFont.Weight.DemiBold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.title_label)

        # Gradient background
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#202020"))
        gradient.setColorAt(1.0, QColor("#202020"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Input for adding a project
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

        # List of projects
        self.projects_list = ListWidget()
        self.projects_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.projects_list.customContextMenuRequested.connect(self.open_context_menu)
        self.projects_list.itemClicked.connect(self.open_project)
        self.layout.addWidget(self.projects_list)

        # Back button (optional)
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

        # Load initial projects
        self.load_projects()

    def template_card(self):
        temp_dialog = CardButtonDialog(image_path="resources/icons/NTA.png", button_text="JEE")
        temp_dialog.exec()

    def load_projects(self):
        """Load all projects into the list."""
        self.projects_list.clear()
        projects = fetch_projects()
        for project_id, project_name in projects:
            item = QListWidgetItem(project_name)
            item.setData(Qt.ItemDataRole.UserRole, project_id)
            self.projects_list.addItem(item)

    def add_project(self):
        """Add a new project to the database."""
        project_name = self.project_input.text().strip()
        if project_name:
            add_project(project_name)
            self.load_projects()
            self.project_input.clear()

    def open_project(self, item):
        """Open the selected project."""
        project_id = item.data(Qt.ItemDataRole.UserRole)
        self.switch_to_subjects_callback(project_id)

    def open_context_menu(self, position):
        """Open a context menu for the selected project."""
        item = self.projects_list.itemAt(position)
        if item:
            project_id = item.data(Qt.ItemDataRole.UserRole)
            menu = QMenu(self)

            remove_action = menu.addAction("Remove Project")
            remove_action.triggered.connect(lambda: self.remove_project(project_id))

            menu.exec(self.projects_list.mapToGlobal(position))

    def remove_project(self, project_id):
        """Remove the selected project."""
        confirm_deletion = QMessageBox.question(
            self,
            "Confirm Project Deletion",
            f"Are you sure you want to delete this project ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm_deletion == QMessageBox.StandardButton.Yes:
            delete_project(project_id)
            self.load_projects()
