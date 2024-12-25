from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout
from study_db_helpers import add_chapter, fetch_chapters


class ChaptersWidget(QWidget):
    def __init__(self, back_to_subjects_callback):
        super().__init__()
        self.back_to_subjects_callback = back_to_subjects_callback
        self.subject_id = None

        self.setStyleSheet("""
            background-color: #202020;
            color: white;
        """)

        self.layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("Chapters")
        self.title_label.setFont(QFont("Poppins", 24, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Input for adding a chapter
        self.input_layout = QHBoxLayout()
        self.chapter_input = QLineEdit()
        self.chapter_input.setPlaceholderText("Enter a chapter name...")
        self.input_layout.addWidget(self.chapter_input)

        self.add_button = QPushButton("Add Chapter")
        self.add_button.clicked.connect(self.add_chapter)
        self.input_layout.addWidget(self.add_button)
        self.layout.addLayout(self.input_layout)

        # List of chapters
        self.chapters_list = QListWidget()
        self.layout.addWidget(self.chapters_list)

        # Back button
        self.back_button = QPushButton("Back to Subjects")
        self.back_button.clicked.connect(self.back_to_subjects_callback)
        self.layout.addWidget(self.back_button)

    def set_subject(self, subject_id):
        """Set the current subject and load its chapters."""
        self.subject_id = subject_id
        self.load_chapters()

    def load_chapters(self):
        """Load all chapters for the current subject."""
        self.chapters_list.clear()
        if self.subject_id is None:
            return
        chapters = fetch_chapters(self.subject_id)
        for chapter_id, chapter_name in chapters:
            item = QListWidgetItem(chapter_name)
            item.setData(Qt.ItemDataRole.UserRole, chapter_id)
            self.chapters_list.addItem(item)

    def add_chapter(self):
        """Add a new chapter to the current subject."""
        chapter_name = self.chapter_input.text().strip()
        if chapter_name and self.subject_id:
            add_chapter(self.subject_id, chapter_name)
            self.load_chapters()
            self.chapter_input.clear()
