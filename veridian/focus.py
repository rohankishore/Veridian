import os
import sqlite3
from datetime import datetime, timedelta

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

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QDateEdit, QLabel
from PyQt6.QtCore import QDate


class FocusSessionFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Focus Sessions")

        layout = QVBoxLayout()

        self.filter_label = QLabel("Select Time Filter:")
        layout.addWidget(self.filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Time", "Today", "This Week", "This Month", "Custom Range"])
        layout.addWidget(self.filter_combo)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setEnabled(False)
        layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setEnabled(False)
        layout.addWidget(self.end_date)

        self.apply_button = QPushButton("Apply Filter")
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

        # Connect signals
        self.filter_combo.currentIndexChanged.connect(self.toggle_date_inputs)
        self.apply_button.clicked.connect(self.accept)  # Close dialog on apply

    def toggle_date_inputs(self):
        """ Enable date inputs only for custom range selection """
        if self.filter_combo.currentText() == "Custom Range":
            self.start_date.setEnabled(True)
            self.end_date.setEnabled(True)
        else:
            self.start_date.setEnabled(False)
            self.end_date.setEnabled(False)

    def get_selected_filter(self):
        """ Return selected filter option and date range if applicable """
        filter_option = self.filter_combo.currentText()
        if filter_option == "Custom Range":
            return filter_option, self.start_date.date().toString("yyyy-MM-dd"), self.end_date.date().toString(
                "yyyy-MM-dd")
        return filter_option, None, None


def get_filtered_sessions(filter_option, start_date=None, end_date=None):
    conn = sqlite3.connect("focus_data.db")
    cursor = conn.cursor()

    query = "SELECT * FROM focus_sessions"
    conditions = []
    params = []

    if filter_option == "Today":
        today = datetime.now().strftime("%Y-%m-%d")
        conditions.append("date = ?")
        params.append(today)

    elif filter_option == "This Week":
        start_of_week = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        conditions.append("date >= ?")
        params.append(start_of_week)

    elif filter_option == "This Month":
        start_of_month = datetime.now().strftime("%Y-%m-01")
        conditions.append("date >= ?")
        params.append(start_of_month)

    elif filter_option == "Custom Range" and start_date and end_date:
        conditions.append("date BETWEEN ? AND ?")
        params.extend([start_date, end_date])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results


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

    def show_filtered_sessions(self):
        dialog = FocusSessionFilterDialog(self)
        if dialog.exec():
            filter_option, start_date, end_date = dialog.get_selected_filter()
            sessions = get_filtered_sessions(filter_option, start_date, end_date)

            # Display filtered sessions
            print("Filtered Sessions:", sessions)

    def init_db(self):
        # Connect to SQLite database or create it if it doesn't exist
        self.conn = sqlite3.connect('resources/data/focus_data.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                duration INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='focus_sessions'")
        table_exists = self.cursor.fetchone()
        print("Table Exists:", table_exists)

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

    def save_focus_session(self):
        print("save focus session... entered")
        if self.focus_start_time is None:
            print("Focus start time is None. Skipping save.")
            return

        focus_name = self.focus_name_input.text().strip() or "Untitled Session"
        end_time = QTime.currentTime()
        actual_duration = self.focus_start_time.msecsTo(end_time) // 1000  # Convert to seconds
        focus_date = QDate.currentDate().toString("yyyy-MM-dd")
        start_time_str = self.focus_start_time.toString("hh:mm:ss")

        try:
            self.cursor.execute(
                "INSERT INTO focus_sessions (name, duration, start_time, date) VALUES (?, ?, ?, ?)",
                (focus_name, actual_duration, start_time_str, focus_date)
            )
            self.conn.commit()
            print("✅ Insert Successful!")
        except sqlite3.Error as e:
            print("❌ Database Insert Error:", e)

        print(f"DEBUG - Name: {focus_name}, Duration: {actual_duration}s, Start: {start_time_str}, Date: {focus_date}")

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
            self.save_focus_session()
            print("🔹 Focus Start Time:", self.focus_start_time)
            # Save the session

    def reset_timer(self):
        # Reset the timer based on selected time or stopwatch
        self.timer.stop()
        self.save_focus_session()
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
        dialog = QDialog(self)
        dialog.setWindowTitle("Focus Session Statistics")
        dialog.setModal(True)
        dialog_layout = QVBoxLayout(dialog)

        # Fetch data from the database
        self.cursor.execute("SELECT name, SUM(duration) FROM focus_sessions GROUP BY name")
        data = self.cursor.fetchall()

        if not data:
            QMessageBox.information(self, "No Data", "No focus session data available.")
            return

        # Extract session names and total durations (convert to minutes)
        session_names = [row[0] for row in data]
        durations = [row[1] / 60 for row in data]  # Convert seconds to minutes

        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(session_names, durations, color="#4CAF50")  # Horizontal bar chart
        ax.set_xlabel("Total Focus Time (minutes)")
        ax.set_ylabel("Session Name")
        ax.set_title("Focus Session Statistics")
        ax.grid(axis="x", linestyle="--", alpha=0.7)

        # Create Matplotlib figure canvas
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
