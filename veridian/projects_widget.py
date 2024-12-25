from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPalette, QBrush
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidgetItem, QHBoxLayout, QMenu, QMessageBox
from qfluentwidgets import (ListWidget, LineEdit, PushButton, MessageBox)

from study_db_helpers import add_project, fetch_projects, delete_project


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
