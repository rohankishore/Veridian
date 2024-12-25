from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox, QListWidgetItem
from qfluentwidgets import ListWidget, PushButton, LineEdit
from study_db_helpers import fetch_chapters, update_chapter_completion, add_chapter_to_db



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
        self.title_label.setFont(QFont("Poppins", 36, QFont.Weight.DemiBold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.title_label)

        # List of chapters
        self.chapters_list = ListWidget()
        self.layout.addWidget(self.chapters_list)

        # Add Chapter Section
        self.chapter_input = LineEdit()
        self.chapter_input.setPlaceholderText("Enter a new chapter...")
        self.chapter_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 5px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #ffffff;
            }
        """)
        self.layout.addWidget(self.chapter_input)

        self.add_chapter_button = PushButton("Add Chapter")
        self.add_chapter_button.setStyleSheet("""
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
        self.add_chapter_button.clicked.connect(self.add_chapter)
        self.layout.addWidget(self.add_chapter_button)

        # Back button
        self.back_button = PushButton("Back to Subjects")
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
        self.back_button.clicked.connect(self.back_to_subjects_callback)
        self.layout.addWidget(self.back_button)

    def set_subject(self, subject_id):
        """Set the current subject and load its chapters."""
        self.subject_id = subject_id
        self.load_chapters()

    def load_chapters(self):
        """Load all chapters for the current subject."""
        self.chapters_list.clear()  # Clear previous chapters
        chapters = fetch_chapters(self.subject_id)  # Fetch chapters from the database

        for chapter_id, chapter_name, is_complete in chapters:
            self.add_chapter_to_list(chapter_id, chapter_name, is_complete)

    def add_chapter_to_list(self, chapter_id, name, completed):
        chapter_widget = ChapterItemWidget(chapter_id, name, completed, self.toggle_chapter_completion)
        chapter_item = QListWidgetItem()
        chapter_item.setSizeHint(chapter_widget.sizeHint())
        self.chapters_list.addItem(chapter_item)
        self.chapters_list.setItemWidget(chapter_item, chapter_widget)

    def add_chapter(self):
        chapter_name = self.chapter_input.text().strip()
        if chapter_name:
            try:
                add_chapter_to_db(self.subject_id, chapter_name)
            except Exception as e:
                print(f"Error adding chapter: {e}")
            # Clear the input and reload the chapters list
            self.chapter_input.clear()
            self.load_chapters()

    def toggle_chapter_completion(self, chapter_id, is_complete):
        """Toggle the completion status of a chapter."""
        update_chapter_completion(chapter_id, is_complete)  # Update the database
        self.load_chapters()
