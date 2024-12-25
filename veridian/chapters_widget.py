from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox, QListWidgetItem
from qfluentwidgets import ListWidget, PushButton, CheckBox

from study_db_helpers import fetch_chapters, update_chapter_completion


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
        print(f"Setting subject with ID: {subject_id}")  # Debug print
        self.subject_id = subject_id
        self.load_chapters()

    def load_chapters(self):
        """Load all chapters for the current subject."""
        print(f"Loading chapters for subject ID: {self.subject_id}")  # Debug print
        self.chapters_list.clear()  # Clear previous chapters
        try:
            chapters = fetch_chapters(self.subject_id)  # Fetch chapters from the database
        except Exception as e:
            print(f"Error fetching chapters: {e}")  # Debug print
            return

        print(f"Fetched chapters: {chapters}")  # Debug print

        if not chapters:
            print("No chapters found for this subject.")  # Debug print

        for chapter_id, chapter_name, is_complete in chapters:
            print(f"Processing chapter: ID={chapter_id}, Name={chapter_name}, Completed={is_complete}")  # Debug print

            chapter_layout = QHBoxLayout()

            # Chapter name
            chapter_label = QLabel(chapter_name)
            chapter_label.setFont(QFont("Poppins", 16))
            chapter_layout.addWidget(chapter_label)

            # Checkbox for completion
            checkbox = QCheckBox()
            checkbox.setChecked(is_complete)  # Set checkbox based on completion
            checkbox.toggled.connect(
                lambda checked, cid=chapter_id: self.toggle_completion(cid, checked)
            )  # Update completion in the database
            chapter_layout.addWidget(checkbox)

            # Create a QWidget and set the layout for this chapter
            chapter_widget = QWidget()
            chapter_widget.setLayout(chapter_layout)

            # Create a QListWidgetItem and set the widget
            try:
                chapter_item = QListWidgetItem(self.chapters_list)
                print(f"Created QListWidgetItem for chapter: {chapter_name}")  # Debug print
                self.chapters_list.addItem(chapter_item)  # Add item first
                self.chapters_list.setItemWidget(chapter_item, chapter_widget)  # Now set the widget to this item
                print(f"Added chapter: {chapter_name} to the list.")  # Debug print
            except Exception as e:
                print(f"Error adding chapter to list: {e}")  # Debug print

    def toggle_completion(self, chapter_id, is_complete):
        """Toggle the completion status of a chapter."""
        print(f"Toggling completion for chapter ID={chapter_id} to {is_complete}")  # Debug print
        update_chapter_completion(chapter_id, is_complete)  # Update the database
