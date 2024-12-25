from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox, QListWidgetItem
from qfluentwidgets import ListWidget, PushButton, LineEdit
from study_db_helpers import fetch_chapters, update_chapter_completion, add_chapter_to_db
from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPalette, QBrush



class ChapterItemWidget(QWidget):
    """A widget representing a chapter item."""

    def __init__(self, chapter_id, name, completed, toggle_completion_callback):
        super().__init__()
        self.chapter_id = chapter_id
        self.completed = completed
        self.toggle_completion_callback = toggle_completion_callback

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Chapter Name Label
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet(f"color: {'#68E95C' if completed else '#ffffff'}; font-size: 16px;")
        layout.addWidget(self.name_label)

        # Tick Button
        self.tick_button = PushButton("✔")
        self.tick_button.setFixedSize(30, 30)
        self.tick_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#68E95C' if completed else '#333333'};
                color: #ffffff;
                border-radius: 5px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #444444;
            }}
        """)
        self.tick_button.clicked.connect(self.toggle_completion)
        layout.addWidget(self.tick_button)

    def toggle_completion(self):
        self.completed = not self.completed
        self.toggle_completion_callback(self.chapter_id, self.completed)

        # Update UI appearance
        self.name_label.setStyleSheet(f"color: {'#68E95C' if self.completed else '#ffffff'}; font-size: 16px;")
        self.tick_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#68E95C' if self.completed else '#333333'};
                color: #ffffff;
                border-radius: 5px;
                font-size: 14px;
            }}
        """)


class ChaptersWidget(QWidget):
    def __init__(self, show_subtopics_callback, back_to_subjects_callback):
        super().__init__()
        self.show_subtopics_callback = show_subtopics_callback  # Callback for navigating to subtopics
        self.back_to_subjects_callback = back_to_subjects_callback
        self.subject_id = None

        self.layout = QVBoxLayout(self)

        # Gradient Background
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#202020"))
        gradient.setColorAt(1.0, QColor("#202020"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Title
        self.title_label = QLabel("Chapters")
        self.title_label.setFont(QFont("Poppins", 36, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet("color: #ffffff; margin-bottom: 20px;")
        self.layout.addWidget(self.title_label)

        # List of chapters
        self.chapters_list = ListWidget()
        self.chapters_list.itemClicked.connect(self.open_subtopics)  # Navigate on item click
        self.layout.addWidget(self.chapters_list)

        # Chapter input and button
        self.chapter_input = LineEdit()
        self.chapter_input.setPlaceholderText("Enter new chapter...")
        self.layout.addWidget(self.chapter_input)

        self.add_chapter_button = PushButton("Add Chapter")
        self.add_chapter_button.clicked.connect(self.add_chapter)
        self.layout.addWidget(self.add_chapter_button)

        # Back button
        self.back_button = PushButton("Back to Subjects")
        self.back_button.clicked.connect(self.back_to_subjects_callback)
        self.layout.addWidget(self.back_button)

    def set_subject(self, subject_id):
        """Set the current subject and load its chapters."""
        self.subject_id = subject_id
        self.load_chapters()

    def load_chapters(self):
        """Load chapters for the selected subject."""
        self.chapters_list.clear()
        chapters = fetch_chapters(self.subject_id)
        for chapter_id, chapter_name, is_complete in chapters:
            chapter_widget = ChapterItemWidget(chapter_id, chapter_name, is_complete, self.toggle_chapter_completion)
            chapter_item = QListWidgetItem()
            chapter_item.setSizeHint(chapter_widget.sizeHint())
            self.chapters_list.addItem(chapter_item)
            self.chapters_list.setItemWidget(chapter_item, chapter_widget)

    def add_chapter(self):
        """Add a new chapter."""
        chapter_name = self.chapter_input.text().strip()
        if chapter_name:
            add_chapter_to_db(self.subject_id, chapter_name)
            self.chapter_input.clear()
            self.load_chapters()

    def toggle_chapter_completion(self, chapter_id, is_complete):
        """Toggle completion status for a chapter."""
        update_chapter_completion(chapter_id, is_complete)
        self.load_chapters()

    def open_subtopics(self, item):
        """Navigate to the Subtopics screen."""
        chapter_widget = self.chapters_list.itemWidget(item)
        self.show_subtopics_callback(chapter_widget.chapter_id, chapter_widget.name_label.text())