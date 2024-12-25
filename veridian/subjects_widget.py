from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout
from study_db_helpers import add_subject, fetch_subjects


class SubjectsWidget(QWidget):
    def __init__(self, switch_to_chapters_callback, back_to_projects_callback):
        super().__init__()
        self.switch_to_chapters_callback = switch_to_chapters_callback
        self.back_to_projects_callback = back_to_projects_callback
        self.project_id = None

        self.setStyleSheet("""
            background-color: #202020;
            color: white;
        """)

        self.layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("Subjects")
        self.title_label.setFont(QFont("Poppins", 24, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Input for adding a subject
        self.input_layout = QHBoxLayout()
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter a subject name...")
        self.input_layout.addWidget(self.subject_input)

        self.add_button = QPushButton("Add Subject")
        self.add_button.clicked.connect(self.add_subject)
        self.input_layout.addWidget(self.add_button)
        self.layout.addLayout(self.input_layout)

        # List of subjects
        self.subjects_list = QListWidget()
        self.subjects_list.itemClicked.connect(self.open_subject)
        self.layout.addWidget(self.subjects_list)

        # Back button
        self.back_button = QPushButton("Back to Projects")
        self.back_button.clicked.connect(self.back_to_projects_callback)
        self.layout.addWidget(self.back_button)

    def set_project(self, project_id):
        """Set the current project and load its subjects."""
        self.project_id = project_id
        self.load_subjects()

    def load_subjects(self):
        """Load all subjects for the current project."""
        self.subjects_list.clear()
        if self.project_id is None:
            return
        subjects = fetch_subjects(self.project_id)
        for subject_id, subject_name in subjects:
            item = QListWidgetItem(subject_name)
            item.setData(Qt.ItemDataRole.UserRole, subject_id)
            self.subjects_list.addItem(item)

    def add_subject(self):
        """Add a new subject to the current project."""
        subject_name = self.subject_input.text().strip()
        if subject_name and self.project_id:
            add_subject(self.project_id, subject_name)
            self.load_subjects()
            self.subject_input.clear()

    def open_subject(self, item):
        """Open the selected subject."""
        subject_id = item.data(Qt.ItemDataRole.UserRole)
        self.switch_to_chapters_callback(subject_id)
