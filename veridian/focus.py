import os
import sqlite3

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QTimer, QTime, Qt, QDate, QUrl, QSize
from PyQt6.QtGui import QFont, QLinearGradient, QPalette, QBrush, QColor, QIcon
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLineEdit, QDialog, QMessageBox, QScrollArea, QCheckBox)
from qfluentwidgets import (PushButton, LargeTitleLabel, ComboBox, LineEdit, CheckBox)
from qframelesswindow import FramelessWindow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import sqlite3
from PyQt6.QtCore import QTimer, QTime, Qt, QDate
from PyQt6.QtGui import QFont, QLinearGradient, QPalette, QBrush, QColor
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLineEdit, QDialog, QMessageBox)
from qfluentwidgets import (PushButton, LargeTitleLabel, ComboBox, LineEdit, ToggleButton)
from qframelesswindow import FramelessWindow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()

        # Set gradient background for the entire app
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())  # Adjust gradient to span the entire height
        gradient.setColorAt(0.0, QColor("#202020"))  # Top gradient color (darker shade)
        gradient.setColorAt(1.0, QColor("#202020"))  # Bottom gradient color (slightly lighter shade)
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

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

        # Add date column if it doesn't exist
        try:
            self.cursor.execute('''ALTER TABLE focus_sessions ADD COLUMN date TEXT''')
        except sqlite3.OperationalError:
            pass  # If the column already exists, ignore the error

        # Create table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            duration INTEGER,
            start_time TEXT,
            date TEXT
        )''')
        self.conn.commit()

    def add_sample_data(self):
        sample_sessions = [
            ("Math Study", 1500, "2025-01-31T10:00:00", "2025-01-31"),
            ("Project Work", 1800, "2025-01-31T11:00:00", "2025-01-31"),
            ("Reading", 1200, "2025-01-31T12:00:00", "2025-01-31"),
            ("Coding", 2000, "2025-01-31T13:00:00", "2025-01-31"),
            ("Exercise", 900, "2025-01-31T14:00:00", "2025-01-31")
        ]

        self.cursor.executemany("INSERT INTO focus_sessions (name, duration, start_time, date) VALUES (?, ?, ?, ?)",
                                sample_sessions)
        self.conn.commit()

    def save_focus_session(self):
        session_name = self.session_name_label.text()
        if not session_name or session_name == "Focus":  # Handle default name
            session_name = "Unnamed Session"

        end_time = QTime.currentTime()
        duration_seconds = self.focus_start_time.secsTo(end_time)
        current_date = QDate.currentDate().toString("yyyy-MM-dd")  # Get the current date

        # Insert session data with the date
        self.cursor.execute("INSERT INTO focus_sessions (name, duration, start_time, date) VALUES (?, ?, ?, ?)",
                            (session_name, duration_seconds, self.focus_start_time.toString(Qt.DateFormat.ISODate),
                             current_date))
        self.conn.commit()

    def update_time_label(self):
        # Update the label with the current time in mm:ss format
        self.time_label.setText(self.time_left.toString("mm:ss"))

    def start_timer(self):
        self.focus_start_time = QTime.currentTime()  # Record start time
        focus_name = self.focus_name_input.text()
        self.session_name_label.setText(focus_name)
        self.timer.start(1000)  # Start the timer with 1-second interval
        self.start_button.setDisabled(True)

        # Start music only if the checkbox is checked
        if self.music_toggle.isChecked():
            self.play_music()

        # Hide the buttons and the focus name input when the timer starts
        self.start_button.setVisible(False)
        self.time_selector.setVisible(False)
        self.focus_name_input.setVisible(False)
        self.stats_button.setVisible(False)

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
            self.start_button.setVisible(True)  # Show start button again
            self.focus_name_input.setVisible(True)  # Show the focus name input again
            self.stats_button.setVisible(True)  # Show the statistics button again
            self.save_focus_session()  # Save the session

    def reset_timer(self):
        # Reset the timer based on selected time or stopwatch
        self.timer.stop()
        self.media_player.stop()
        self.session_name_label.setText("Focus")
        if self.is_stopwatch:
            self.time_left = QTime(0, 0, 0)  # Reset to 00:00:00 for stopwatch
        else:
            self.time_left = QTime(0, self.selected_time, 0)  # Reset to selected Pomodoro time
        self.update_time_label()
        self.start_button.setEnabled(True)

        # Show the buttons again when the timer is reset
        self.start_button.setVisible(True)
        self.time_selector.setVisible(True)
        self.focus_name_input.setVisible(True)
        self.stats_button.setVisible(True)

    def toggle_music(self, state):
        try:
            if state == Qt.CheckState.Checked.value:
                self.music_selector.setEnabled(True)  # Enable selection
                self.music_selector.setVisible(True)  # Make the music selector visible
            else:
                self.music_selector.setEnabled(False)
                self.music_selector.setVisible(False)  # Hide the music selector when unchecked
                self.media_player.stop()  # Stop music when unchecked
        except Exception as e:
            print(f"Error toggling music: {e}")

    def get_music_files(self):
        music_dir = "resources/music/"
        return [f for f in os.listdir(music_dir) if f.endswith(".mp3")]

    def play_music(self):
        selected_music = self.music_selector.currentText()
        if selected_music:
            file_path = f"resources/music/{selected_music}"
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.media_player.play()

    def change_music(self):
        if self.music_toggle.isChecked():
            self.play_music()


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
        dialog.setModal(True)  # Make the dialog modal so it blocks interaction with the main window
        dialog_layout = QVBoxLayout(dialog)

        # Fetch data from the database for all sessions
        self.cursor.execute("SELECT name, duration, date FROM focus_sessions")
        data = self.cursor.fetchall()

        if not data:
            QMessageBox.information(self, "No Data", "No focus session data available.")
            return

        # Prepare weekly data
        weekly_data = {}
        for name, duration, date in data:
            week_start = QDate.fromString(date, Qt.DateFormat.ISODate).addDays(
                -QDate.fromString(date, Qt.DateFormat.ISODate).dayOfWeek() + 1)
            week_key = week_start.toString(Qt.DateFormat.ISODate)

            if week_key not in weekly_data:
                weekly_data[week_key] = 0
            weekly_data[week_key] += duration / 60  # Convert to minutes

        # Plot weekly data
        weeks = list(weekly_data.keys())
        durations = list(weekly_data.values())

        fig, ax = plt.subplots()
        ax.bar(weeks, durations)
        ax.set_xlabel("Week")
        ax.set_ylabel("Focus Duration (minutes)")
        ax.set_title("Focus Duration per Week")

        # Create a Matplotlib figure and canvas
        canvas = FigureCanvas(fig)
        dialog_layout.addWidget(canvas)

        dialog.exec()

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        if hasattr(self, 'conn'):  # Check if the connection exists
            self.conn.close()
        event.accept()

    def init_ui(self):
        # Make the window borderless
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Create a layout
        layout = QVBoxLayout(self)

        # Create the main layout (no scroll area)
        scroll_widget = QWidget(self)
        layout.addWidget(scroll_widget)

        # Apply gradient to the scroll widget
        scroll_palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())  # Adjust gradient to span the entire height
        gradient.setColorAt(0.0, QColor("#202020"))  # Top gradient color (darker shade)
        gradient.setColorAt(1.0, QColor("#202020"))  # Bottom gradient color (slightly lighter shade)
        scroll_palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        scroll_widget.setPalette(scroll_palette)
        scroll_widget.setAutoFillBackground(True)

        # Create the layout for the scroll widget
        scroll_layout = QVBoxLayout(scroll_widget)

        # Focus session name input
        self.focus_name_input = LineEdit(self)
        self.focus_name_input.setPlaceholderText("What'd you like to focus on? ")

        # Focus session name display (Initially empty)
        self.session_name_label = LargeTitleLabel(self)
        self.session_name_label.setFont(QFont("Poppins", 28, QFont.Weight.DemiBold))
        self.session_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_name_label.setText("Focus")  # Default text
        scroll_layout.addWidget(self.session_name_label)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        self.music_toggle = CheckBox()
        self.music_toggle.setText("Background Music")
        self.music_toggle.stateChanged.connect(self.toggle_music)

        self.music_selector = ComboBox()
        self.music_selector.setVisible(False)
        self.music_selector.addItems(self.get_music_files())
        self.music_selector.setEnabled(False)
        self.music_selector.currentIndexChanged.connect(self.change_music)

        # Timer label
        self.time_label = LargeTitleLabel(self)
        self.time_label.setFont(QFont("Poppins", 40, QFont.Weight.ExtraBold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_time_label()
        scroll_layout.addWidget(self.time_label)

        # Time Selection
        self.time_selector = ComboBox(self)
        self.time_selector.addItems(["15 minutes", "25 minutes", "30 minutes", "45 minutes", "Stopwatch"])
        self.time_selector.currentIndexChanged.connect(self.update_selected_time)
        scroll_layout.addWidget(self.focus_name_input)
        scroll_layout.addWidget(self.time_selector)
        scroll_layout.addWidget(self.music_toggle)
        scroll_layout.addWidget(self.music_selector)


        # Control buttons
        button_layout = QHBoxLayout()

        self.start_button = PushButton(self)
        start_icon = QIcon("resources/icons/start.png")
        self.start_button.setIconSize(QSize(48, 48))  # Adjust icon size as needed
        self.start_button.setFixedSize(48, 48)
        self.start_button.setIcon(start_icon)
        self.start_button.setStyleSheet("""
            QPushButton {
                background : none;
                font-size: 18px;
                border-radius: 24px;
                padding: 12px 20px;
                color: #333333;
            }
            QPushButton:hover {
                background: none;
                border-width: 2pc;
                border-color : #3e9e3b;
                }
        """)
        self.start_button.clicked.connect(self.start_timer)
        button_layout.addWidget(self.start_button)

        self.reset_button = PushButton(self)
        reset_icon = QIcon("resources/icons/stop.png")
        self.reset_button.setIconSize(QSize(48, 48))  # Adjust icon size as needed
        self.reset_button.setFixedSize(50, 50)
        self.reset_button.setIcon(reset_icon)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background: none;
                font-size: 18px;
                border-radius: 12px;
                padding: 12px 20px;
                color: #333333;
            }
            QPushButton:hover {
                background: none;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.reset_button.clicked.connect(self.reset_timer)
        button_layout.addWidget(self.reset_button)

        scroll_layout.addLayout(button_layout)

        # Focus Statistics Button
        self.stats_button = PushButton("Focus Statistics", self)
        self.stats_button.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                font-size: 16px;
                border-radius: 12px;
                padding: 10px 15px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
            QPushButton:pressed {
                background-color: #2c6fca;
            }
        """)
        self.stats_button.clicked.connect(self.show_statistics)
        scroll_layout.addWidget(self.stats_button)

        self.setLayout(layout)
