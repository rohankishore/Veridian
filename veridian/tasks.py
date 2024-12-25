# coding:utf-8

# import qdarktheme
import sqlite3

# import qdarktheme
from PyQt6.QtCore import Qt, QPropertyAnimation
from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPalette, QBrush
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QListWidgetItem, QLabel
from qfluentwidgets import (LargeTitleLabel, ListWidget, LineEdit, PushButton)


# Database helper functions
def initialize_database():
    connection = sqlite3.connect("resources/data/habits.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0
        )
    """)
    connection.commit()
    connection.close()

def delete_habit_from_db(habit_id):
    connection = sqlite3.connect("resources/data/habits.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    connection.commit()
    connection.close()

def fetch_habits():
    connection = sqlite3.connect("resources/data/habits.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, streak, completed FROM habits")
    habits = cursor.fetchall()
    connection.close()
    return habits


def toggle_completion(self):
    self.completed = not self.completed
    self.toggle_completion_callback(self.habit_id, self.completed)

    # Update UI appearance
    self.name_label.setStyleSheet(f"color: {'#68E95C' if self.completed else '#ffffff'}; font-size: 16px;")
    self.tick_button.setStyleSheet(f"""
        QPushButton {{
            background-color: {'#68E95C' if self.completed else '#333333'};
            color: #ffffff;
            border-radius: 5px;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: #444444;
        }}
    """)

def toggle_habit_completion(habit_id, completed):
    connection = sqlite3.connect("resources/data/habits.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE habits SET completed = ? WHERE id = ?", (1 if completed else 0, habit_id))
    connection.commit()
    connection.close()


class HabitItemWidget(QWidget):
    def __init__(self, habit_id, name, completed, toggle_completion_callback):
        super().__init__()
        self.habit_id = habit_id
        self.completed = completed
        self.toggle_completion_callback = toggle_completion_callback

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Habit Name Label
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
        self.toggle_completion_callback(self.habit_id, self.completed)


class HabitsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Veridian")
        self.setMinimumSize(800, 600)
        self.setObjectName("habits-page")

        # Gradient Background
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#202020"))
        gradient.setColorAt(1.0, QColor("#202020"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)

        # Title
        self.title_label = LargeTitleLabel()
        self.title_label.setText("Tasks")
        self.title_label.setFont(QFont("Poppins", 36, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet("color: #ffffff; margin-bottom: 20px;")
        self.main_layout.addWidget(self.title_label)

        # Habit List
        self.habit_list = ListWidget()
        self.habit_list.setStyleSheet("background-color: #202020; color: #ffffff; border-radius: 8px;")
        self.habit_list.setSpacing(10)
        self.main_layout.addWidget(self.habit_list)

        # Add Habit Section
        self.habit_input = LineEdit()
        self.habit_input.setPlaceholderText("Enter a new task...")
        self.habit_input.setStyleSheet("""
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
        self.main_layout.addWidget(self.habit_input)

        self.add_habit_button = PushButton()
        self.add_habit_button.setText("Add Task")
        self.add_habit_button.setStyleSheet("""
            QPushButton {
                background-color: #68E95C;
                color: #ffffff;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3700b3;
            }
        """)
        self.add_habit_button.clicked.connect(self.add_habit)
        self.main_layout.addWidget(self.add_habit_button)

        # Load habits from the database
        self.load_habits()

    def load_habits(self):
        habits = fetch_habits()  # Fetch updated tasks
        self.habit_list.clear()  # Clear the list first

        for habit in habits:
            self.add_habit_to_list(habit[0], habit[1], habit[3])  # Load each habit

    def add_habit_to_db(self, name):
        connection = sqlite3.connect("resources/data/habits.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO habits (name, completed) VALUES (?, ?)", (name, 0))
        connection.commit()
        connection.close()

    def add_habit(self):
        habit_name = self.habit_input.text().strip()
        if habit_name:
            self.add_habit_to_db(habit_name)
            self.habit_input.clear()
            self.load_habits()

    def add_habit_to_list(self, habit_id, name, completed):
        habit_widget = HabitItemWidget(habit_id, name, completed, self.toggle_habit_completion)
        habit_item = QListWidgetItem()
        habit_item.setSizeHint(habit_widget.sizeHint())
        self.habit_list.addItem(habit_item)
        self.habit_list.setItemWidget(habit_item, habit_widget)

    def toggle_habit_completion(self, habit_id, completed):
        toggle_habit_completion(habit_id, completed)
        # Refresh the list to reflect the changes
        self.load_habits()
