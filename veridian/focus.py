import sqlite3
from PyQt6.QtCore import QTimer, QTime, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLineEdit, QDialog, QMessageBox)
from qfluentwidgets import (PushButton, LargeTitleLabel, ComboBox, LineEdit)
from qframelesswindow import FramelessWindow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Focus")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.time_left = QTime(0, 15, 0)  # Default time to 15 minutes
        self.selected_time = 25  # Store selected time in minutes
        self.is_stopwatch = False  # Flag to indicate if Stopwatch is selected
        self.is_running = False  # Flag to track if timer is running
        self.focus_start_time = None  # Store the start time of the focus session

        self.init_db()  # Initialize the database
        self.init_ui()

    def init_db(self):
        # Connect to SQLite database or create it if it doesn't exist
        self.conn = sqlite3.connect('resources/data/focus_data.db')
        self.cursor = self.conn.cursor()

        self.add_sample_data()


        # Create a table to store session data (name, duration, and start time)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            duration INTEGER,  -- Store duration in seconds
            start_time TEXT
        )''')
        self.conn.commit()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Focus session name input
        self.focus_name_input = LineEdit(self)
        self.focus_name_input.setPlaceholderText("What'd you like to focus on? ")

        # Focus session name display (Initially empty)
        self.session_name_label = LargeTitleLabel(self)
        self.session_name_label.setFont(QFont("Poppins", 24, QFont.Weight.DemiBold))
        self.session_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_name_label.setText("Current Focus Session")  # Default text
        layout.addWidget(self.session_name_label)

        # Timer label
        self.time_label = LargeTitleLabel(self)
        self.time_label.setFont(QFont("Poppins", 30, QFont.Weight.DemiBold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_time_label()
        layout.addWidget(self.time_label)

        # Time Selection
        self.time_selector = ComboBox(self)
        self.time_selector.addItems(["15 minutes", "25 minutes", "30 minutes", "45 minutes", "Stopwatch"])
        self.time_selector.currentIndexChanged.connect(self.update_selected_time)
        layout.addWidget(self.focus_name_input)
        layout.addWidget(self.time_selector)

        # Control buttons
        button_layout = QHBoxLayout()

        self.start_button = PushButton("Start Focus Now", self)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #68E95C;
                font-size: 18px;
                border-radius: 12px;
                padding: 12px 20px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #51b547;
            }
            QPushButton:pressed {
                background-color: #3e9e3b;
            }
        """)
        self.start_button.clicked.connect(self.start_timer)
        button_layout.addWidget(self.start_button)

        self.reset_button = PushButton("Reset", self)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                font-size: 18px;
                border-radius: 12px;
                padding: 12px 20px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.reset_button.clicked.connect(self.reset_timer)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)

        # Focus Statistics Button
        self.stats_button = PushButton("Focus Statistics", self)
        self.stats_button.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                font-size: 16px;
                border-radius: 12px;
                padding: 10px 15px;
                color: white;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
            QPushButton:pressed {
                background-color: #2c6fca;
            }
        """)
        self.stats_button.clicked.connect(self.show_statistics)
        layout.addWidget(self.stats_button)

    def start_timer(self):
        self.focus_start_time = QTime.currentTime()  # Record start time
        self.timer.start(1000)  # Start the timer with 1-second interval
        self.start_button.setDisabled(True)

    def update_timer(self):
        # Decrease the time left by one second in Pomodoro mode
        if not self.is_stopwatch:
            self.time_left = self.time_left.addSecs(-1)
        else:
            self.time_left = self.time_left.addSecs(1)

        self.update_time_label()

        # If time is up (Pomodoro mode), stop the timer
        if not self.is_stopwatch and self.time_left == QTime(0, 0, 0):
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.save_focus_session()  # Save the session

    def add_sample_data(self):
        sample_sessions = [
            ("Math Study", 1500, "2025-01-31T10:00:00"),
            ("Project Work", 1800, "2025-01-31T11:00:00"),
            ("Reading", 1200, "2025-01-31T12:00:00"),
            ("Coding", 2000, "2025-01-31T13:00:00"),
            ("Exercise", 900, "2025-01-31T14:00:00")
        ]

        self.cursor.executemany("INSERT INTO focus_sessions (name, duration, start_time) VALUES (?, ?, ?)",
                                sample_sessions)
        self.conn.commit()

    def save_focus_session(self):
        session_name = self.session_name_label.text()
        if not session_name or session_name == "Focus":  # Handle default name
            session_name = "Unnamed Session"

        end_time = QTime.currentTime()
        duration_seconds = self.focus_start_time.secsTo(end_time)

        self.cursor.execute("INSERT INTO focus_sessions (name, duration, start_time) VALUES (?, ?, ?)",
                            (session_name, duration_seconds, self.focus_start_time.toString(Qt.DateFormat.ISODate)))
        self.conn.commit()

    def update_time_label(self):
        # Update the label with the current time in mm:ss format
        self.time_label.setText(self.time_left.toString("mm:ss"))

    def reset_timer(self):
        # Reset the timer based on selected time or stopwatch
        self.timer.stop()
        if self.is_stopwatch:
            self.time_left = QTime(0, 0, 0)  # Reset to 00:00:00 for stopwatch
        else:
            self.time_left = QTime(0, self.selected_time, 0)  # Reset to selected Pomodoro time
        self.update_time_label()
        self.start_button.setEnabled(True)

    def update_selected_time(self):
        # Update the selected time based on the dropdown choice
        selected_text = self.time_selector.currentText()

        if selected_text == "Stopwatch":
            self.is_stopwatch = True
            self.time_left = QTime(0, 0, 0)  # Reset to zero for Stopwatch
        else:
            self.is_stopwatch = False
            if "15" in selected_text:
                self.selected_time = 15
            elif "25" in selected_text:
                self.selected_time = 25
            elif "30" in selected_text:
                self.selected_time = 30
            elif "45" in selected_text:
                self.selected_time = 45

        # Reset timer based on the selection
        self.reset_timer()

    def show_statistics(self):
        # Open statistics dialog with pie chart
        dialog = QDialog(self)
        dialog.setWindowTitle("Focus Session Statistics")
        dialog_layout = QVBoxLayout(dialog)

        # Fetch data from the database
        self.cursor.execute("SELECT name, duration FROM focus_sessions")
        data = self.cursor.fetchall()

        if not data:
            QMessageBox.information(self, "No Data", "No focus session data available.")
            return

        names = [row[0] for row in data]
        durations = [row[1] / 60 for row in data]  # Convert to minutes

        # Create a Matplotlib figure and canvas
        fig, ax = plt.subplots()
        ax.pie(durations, labels=names, autopct='%1.1f%%', startangle=90)  # Pie chart
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        canvas = FigureCanvas(fig)
        dialog_layout.addWidget(canvas)

        dialog.exec()

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        if hasattr(self, 'conn'):  # Check if the connection exists
            self.conn.close()
        event.accept()
