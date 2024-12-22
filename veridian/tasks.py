# coding:utf-8
import sqlite3

# import qdarktheme
from PyQt6.QtCore import Qt, QPropertyAnimation
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QListWidgetItem
from qfluentwidgets import (LargeTitleLabel, ListWidget, LineEdit)
import os
import sqlite3

# import qdarktheme
from PyQt6.QtCore import Qt, QUrl, QTimer, QSize, QPropertyAnimation
from PyQt6.QtGui import QIcon, QFont, QPixmap, QLinearGradient, QColor, QPalette, QBrush
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy, \
    QSpacerItem, QFileDialog, QWidget, QListWidgetItem, QFrame
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from qfluentwidgets import (Slider, ScrollArea, LargeTitleLabel, ListWidget, LineEdit, PushButton)
import Cards
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Database helper functions
def initialize_database():
    connection = sqlite3.connect("resources/data/habits.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            streak INTEGER DEFAULT 0
        )
    """)
    connection.commit()
    connection.close()


def fetch_habits():
    connection = sqlite3.connect("resources/data/habits.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, streak FROM habits")
    habits = cursor.fetchall()
    connection.close()
    return habits


def add_habit_to_db(name):
    connection = sqlite3.connect("resources/data/habits.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO habits (name) VALUES (?)", (name,))
    connection.commit()
    connection.close()


def update_habit_streak_in_db(habit_id, new_streak):
    connection = sqlite3.connect("resources/data/habits.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE habits SET streak = ? WHERE id = ?", (new_streak, habit_id))
    connection.commit()
    connection.close()


class HabitsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Veridian")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("bakckground-color : #000000")
        self.setObjectName("habits-page")

        # Set gradient background for the entire app
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())  # Adjust gradient to span the entire height
        gradient.setColorAt(0.0, QColor("#1c1c1c"))  # Top gradient color
        gradient.setColorAt(1.0, QColor("#383838"))  # Bottom gradient color
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Main layout
        self.main_layout = QVBoxLayout(self)

        # Title
        self.title_label = LargeTitleLabel()
        self.title_label.setText("Tasks")
        self.title_label.setFont(QFont("Segoe UI Bold", 30))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.main_layout.addWidget(self.title_label)

        # Habit Stats
        self.stats_layout = QHBoxLayout()
        self.main_layout.addLayout(self.stats_layout)

        # Habit List
        self.habit_list = ListWidget()
        self.main_layout.addWidget(self.habit_list)

        # Add Habit Section
        self.habit_input = LineEdit()
        self.habit_input.setPlaceholderText("Enter a new task...")
        self.main_layout.addWidget(self.habit_input)

        self.add_habit_button = PushButton()
        self.add_habit_button.setText("Add Task")
        self.add_habit_button.clicked.connect(self.add_habit)
        self.main_layout.addWidget(self.add_habit_button)

        # Load habits from the database
        self.load_habits()

    def load_habits(self):
        habits = fetch_habits()
        self.habit_list.clear()

        total_habits = len(habits)
        completed_streaks = sum(habit[2] for habit in habits)

        for habit in habits:
            self.add_habit_to_list(habit[0], habit[1], habit[2])

    def add_habit(self):
        habit_name = self.habit_input.text().strip()
        if habit_name:
            add_habit_to_db(habit_name)
            self.habit_input.clear()
            self.load_habits()

    def add_habit_to_list(self, habit_id, name, streak):
        # Create a habit widget
        habit_item = QListWidgetItem(f"{name} - Streak: {streak}")
        self.habit_list.addItem(habit_item)

        # Animate new habit
        self.animate_habit(habit_item)

    def animate_habit(self, habit_item):
        # Example animation for habit widget (fade-in effect)
        habit_widget = self.habit_list.itemWidget(habit_item)
        if not habit_widget:
            return
        animation = QPropertyAnimation(habit_widget, b"opacity")
        animation.setDuration(500)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.start()
