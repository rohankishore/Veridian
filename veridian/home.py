# coding:utf-8
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
from qfluentwidgets import (Slider, ScrollArea, LargeTitleLabel, ListWidget, LineEdit)
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


def fetch_statistics():
    """Fetch total tasks, completed tasks, and total streaks."""
    connection = sqlite3.connect("resources/data/habits.db")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM habits")
    total_tasks = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(completed) FROM habits")
    completed_tasks = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(streak) FROM habits")
    total_streaks = cursor.fetchone()[0] or 0
    connection.close()
    return total_tasks, completed_tasks, total_streaks


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


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Habit Tracker - Dashboard")
        self.setMinimumSize(800, 600)

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
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Title Section
        self.title_label = LargeTitleLabel()
        self.title_label.setFont(QFont("Segoe UI Bold", 30))
        self.title_label.setText("Dashboard")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setStyleSheet("color: #ffffff; margin-bottom: 20px;")
        self.main_layout.addWidget(self.title_label)

        # Statistics Section (Organized Horizontally)
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setContentsMargins(15, 15, 15, 15)

        # Individual Statistic Widgets
        self.total_tasks_label = self.create_stat_label("Total Tasks: 0")
        self.completed_tasks_label = self.create_stat_label("Completed Tasks: 0")
        self.total_streaks_label = self.create_stat_label("Total Streaks: 0")

        # Add statistics to the horizontal layout
        self.stats_layout.addWidget(self.total_tasks_label)
        self.stats_layout.addWidget(self.completed_tasks_label)
        self.stats_layout.addWidget(self.total_streaks_label)

        self.main_layout.addLayout(self.stats_layout)

        # Pie Chart Section
        self.graph_layout = QHBoxLayout()
        self.tasks_layout = QVBoxLayout()
        self.habits_layout = QVBoxLayout()
        self.graph_layout.addLayout(self.tasks_layout)
        self.graph_layout.addLayout(self.habits_layout)
        self.tasks_layout.setContentsMargins(15, 15, 15, 15)
        self.habits_layout.setContentsMargins(15, 15, 15, 15)

        # Pie Chart Widget
        self.canvas = FigureCanvas(Figure(figsize=(5, 5)))
        self.canvas1 = FigureCanvas(Figure(figsize=(5, 5)))

        self.tasks_layout.addWidget(self.canvas)
        self.habits_layout.addWidget(self.canvas1)
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax1 = self.canvas1.figure.add_subplot(111)

        # Set transparent background for the chart figure
        self.canvas.figure.patch.set_facecolor('#1c1c1c')  # Set background color for the whole figure
        self.canvas.figure.patch.set_alpha(1)
        self.canvas.figure.patch.set_facecolor('none')  # No background color for the figure

        self.canvas1.figure.patch.set_facecolor('#1c1c1c')  # Set background color for the whole figure
        self.canvas1.figure.patch.set_alpha(1)
        self.canvas1.figure.patch.set_facecolor('none')

        # Set transparent background for the axes
        self.ax.set_facecolor('none')  # No background color for the axes
        self.ax1.set_facecolor('none')  # No background color for the axes

        self.canvas.setStyleSheet("background: transparent;")
        self.canvas1.setStyleSheet("background: transparent;")

        self.main_layout.addLayout(self.graph_layout)

        # Load statistics and plot the pie chart
        self.load_statistics()
        self.plot_pie_chart()

    def create_stat_label(self, text):
        """Helper function to create styled statistic labels."""
        label = QLabel(text)
        label.setFont(QFont("Arial", 18, QFont.Weight.Medium))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #f5f5f5;")
        return label

    def load_statistics(self):
        total_tasks, completed_tasks, total_streaks = fetch_statistics()
        self.total_tasks_label.setText(f"Total Tasks: {total_tasks}")
        self.completed_tasks_label.setText(f"Completed Tasks: {completed_tasks}")
        self.total_streaks_label.setText(f"Total Streaks: {total_streaks}")

    def plot_pie_chart(self):
        """Plot a pie chart to visualize the proportion of completed vs pending tasks."""
        total_tasks, completed_tasks, _ = fetch_statistics()
        pending_tasks = total_tasks - completed_tasks

        # Data for the pie chart
        labels = ["Completed Tasks", "Pending Tasks"]
        sizes = [completed_tasks, max(pending_tasks, 0)]  # Ensure non-negative values
        colors = ["#1f77b4", "#ff7f0e"]

        self.ax.clear()  # Clear the plot before redrawing
        self.ax1.clear()  # Clear the plot before redrawing

        wedges, texts, autotexts = self.ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            textprops={"color": "white", "fontsize": 12},
        )
        wedges, texts, autotexts = self.ax1.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            textprops={"color": "white", "fontsize": 12},
        )
        self.ax.set_title("", color="#f5f5f5", fontsize=16, pad=20)
        self.canvas.draw()
