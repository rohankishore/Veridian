from PyQt6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPalette, QBrush
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QListWidgetItem, QLabel, QMenu
from qfluentwidgets import (LargeTitleLabel, ListWidget, LineEdit, PushButton)
from projects_widget import ProjectsWidget
from subjects_widget import SubjectsWidget
from veridian.chapters_widget import ChaptersWidget


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
       # self.setMinimumSize(800, 600)
        self.setObjectName("Projects")

        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#202020"))
        gradient.setColorAt(1.0, QColor("#202020"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Stack to manage widgets dynamically
        self.stack = QStackedWidget(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.stack)

        # Initialize Widgets
        self.projects_widget = ProjectsWidget(self.show_subjects)
        self.subjects_widget = SubjectsWidget(self.show_chapters, self.show_projects)
        self.chapters_widget = ChaptersWidget(self.show_subjects)

        # Add widgets to the stack
        self.stack.addWidget(self.projects_widget)
        self.stack.addWidget(self.subjects_widget)
        self.stack.addWidget(self.chapters_widget)

        # Start with the Projects widget
        self.stack.setCurrentWidget(self.projects_widget)

    def show_projects(self):
        """Show the Projects widget."""
        self.stack.setCurrentWidget(self.projects_widget)
        self.projects_widget.load_projects()

    def show_subjects(self, project_id):
        """Show the Subjects widget for a specific project."""
        self.stack.setCurrentWidget(self.subjects_widget)
        self.subjects_widget.set_project(project_id)

    def show_chapters(self, subject_id):
        """Show the Chapters widget for a specific subject."""
        self.stack.setCurrentWidget(self.chapters_widget)
        self.chapters_widget.set_subject(subject_id)
