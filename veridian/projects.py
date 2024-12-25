from PyQt6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPalette, QBrush
from qfluentwidgets import LargeTitleLabel, ListWidget, LineEdit, PushButton
from projects_widget import ProjectsWidget
from subjects_widget import SubjectsWidget
from veridian.chapters_widget import ChaptersWidget


class MainWidget(QWidget):
    """Main widget managing the stack of screens."""

    def __init__(self):
        super().__init__()

        self.setObjectName("projects")

        from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPalette, QBrush
        # Gradient Background
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#202020"))
        gradient.setColorAt(1.0, QColor("#202020"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Setup layout
        self.stack = QStackedWidget(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.stack)
        self.setLayout(self.layout)

        # Initialize Widgets
        self.projects_widget = ProjectsWidget(self.show_subjects)
        self.subjects_widget = SubjectsWidget(self.show_chapters, self.show_projects)
        self.chapters_widget = ChaptersWidget(self.show_projects, self.show_subjects)

        # Add widgets to stack
        self.stack.addWidget(self.projects_widget)
        self.stack.addWidget(self.subjects_widget)
        self.stack.addWidget(self.chapters_widget)

        # Set initial screen
        self.stack.setCurrentWidget(self.projects_widget)

    def show_projects(self):
        """Navigate to the Projects screen."""
        print("Navigating to ProjectsWidget...")
        self.stack.setCurrentWidget(self.projects_widget)

    def show_subjects(self, project_id):
        """Navigate to the Subjects screen and set the project."""
        print(f"Navigating to SubjectsWidget with project_id={project_id}...")
        self.subjects_widget.set_project(project_id)  # Pass the selected project ID
        self.stack.setCurrentWidget(self.subjects_widget)

    def show_chapters(self, subject_id):
        """Navigate to the Chapters screen and set the subject."""
        print(f"Navigating to ChaptersWidget with subject_id={subject_id}...")
        self.chapters_widget.set_subject(subject_id)  # Pass the selected subject ID
        self.stack.setCurrentWidget(self.chapters_widget)
